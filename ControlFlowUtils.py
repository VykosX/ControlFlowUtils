"""
@Author: VykosX
@Description: Custom nodes for ComfyUI to enable flow control with advanced loops, conditional branching, logic operations and several other nifty utilities to enhance your ComfyUI workflows
@Title: ControlFlowUtils
@Nickname: ControlFlowUtils
@Version: 0.2.0 ALPHA
@URL: https://github.com/VykosX/ControlFlowUtils
"""
# UNSTABLE ALPHA RELEASE - EXPECT BUGS TO BITE
# PLEASE DO NOT SHARE OUTSIDE OF LINKING TO THE GITHUB

#Default Python StdLib Imports
import json
import os
import gc
import time
from datetime import datetime
from random import randrange as rnd

#ComfyUI Related Imports
import torch
import nodes
import folder_paths
import comfy.model_management as mem_manager
from comfy_execution.graph import ExecutionBlocker
from server import PromptServer
#from nodes import PreviewImage

#Custom Imports
from . import Types
from .Helpers import *

any_type = Types.AnyType("*")
reverse = slice(None,None,-1)

MAIN_CATEGORY = "🐺 VykosX-ControlFlowUtils"
VYKOSX_STORAGE_DATA = {}

#CUSTOM NODES
#*************
				
'''
CLASS NAME: Cycle
PURPOSE: Allows transmitting cached data to be processed iteratively between multiple queues 
INPUTS:
 - start (Integer):         The initial value for the loop counters
 - step (Integer):          A positive or negative offset to apply to the loop counter on each iteration
 - end (Integer):           The value in which the cycle will be considered to have completed and the Finish flag will be set
 - manual_reset (Boolean):  Toggle this property to have the next cycle be a dry run and re-initialize all parameters. 
							Index, Data and Aux_Data will be set to None for the initial execution
 - auto-reset (Boolean):    Specifies whether the Cycle should reset to the original start value once the cycle is complete
							or keep cycling indefinitely
INTERNAL:
 - state (Dictionary):      Internal variable which gets shared across the cycle and keeps track of its parameters
 - index (Integer):         The current loop index
 - finish (Boolean):        A flag which specifies whether the index has reached the end value
'''
class Cycle:
	def __init__(self):
		self.state = {'index': 0,'step': 1,'end': 0, 'start': 0, 'finish': False, 'auto_reset': True}
		pass

	@classmethod
	def INPUT_TYPES(s):
		return {
			"required": {
				"start": ("INT", {"default": 0,"forceInput": False,"tooltip": "The initial value of the loop counter"}),
				"step": ("INT", {"default": 1,"forceInput": False,"tooltip": "How much the loop counter gets increased or decreased by on each iteration"}),
				"end": ("INT", {"default": 10,"forceInput": False,"tooltip": "The value at which the loop is considered to be finished"})
			},"optional": {
				"manual_reset": ("BOOLEAN", {"forceInput": False,"tooltip": "Enable to force a 'DRY RUN' and reset the Cycle to its first iteration"}),
				"auto_reset": ("BOOLEAN", {"forceInput": False, "default": True, "label_on": "Auto Reset on Cycle End", "label_off": "Keep Cycling until Manual Stop",
				               "tooltip": "Enable to have the loop counter automatically reset to Start once it reaches End"})
			},"hidden": { "unique_id": "UNIQUE_ID" },
		} 
	
	RETURN_TYPES = ("CYCLE","BOOLEAN",)
	RETURN_NAMES = ("CYCLE","RESET?",)
	OUTPUT_TOOLTIPS = ("Connect to the CYCLE input of a [CycleContinue] node to establish a loop","Specifies whether the Cycle is executing its 'DRY RUN' iteration",)
	
	FUNCTION = "run"
	CATEGORY = MAIN_CATEGORY
	DESCRIPTION = \
"""Begins a Cycle, a kind of Loop that gets iterated each time a prompt
is executed. You can use Cycles to send information forwards into subsequent
prompts, allowing for workflows that process data in an iterative manner.

Connect the CYCLE Output of this node to a [Cycle Continue]'s CYCLE Input
to begin the loop.

The first iteration of the loop is called a 'DRY RUN' and Data, Aux_Data
and Index will all be set to None. Additionally the "Reset?" output will
return True so you can test this with an [IF Selector] node to determine
whether you are in the first execution of the loop. You can also trigger
a manual reset to the fist 'DRY RUN' iteration by toggling the Manual_Reset
Input. Use the 'DRY RUN' to reset any variables or the state of your
workflow whenever a fresh Cycle has started.

Set your Start, End and Step parameters to the values you would like to
iterate from, to and by, respectively. If you'd like the loop to return
automatically to the original Start value, enable the Auto_Reset Input,
otherwise the cycle will continue to apply Step to Index on each iteration.

HOVER OVER THE INPUTS AND OUTPUTS OF THE NODE FOR MORE INFO.
"""
	def run(self,start,step,end,manual_reset,auto_reset,unique_id):
	
		debug_print (">> CYCLE [",unique_id,"] INIT!")
			
		#PromptServer.instance.send_sync("VykosX.StartCycle", {"node": node_id})
			
		if manual_reset or self.state['finish']:
			if manual_reset or auto_reset:
			
				debug_print (">> CYCLE [",unique_id,"] RESET!")
			
				self.state = {'index': None,'step':step,'end': end, 'start': start, 'finish': False, 'auto_reset': auto_reset}
				
				return (self.state,True)
				
		return (self.state,False)
	
	@classmethod    
	def IS_CHANGED(self, start ,step, end,manual_reset,auto_reset, unique_id):
		if manual_reset:
			self.state = {'index': start,'step':step,'end': end, 'start': start, 'finish': False, 'auto_reset': auto_reset}
			return True            
		return False

class CycleContinue:
	
	@classmethod
	def INPUT_TYPES(s):
		return {
			"required": {
				"data": (any_type, {"tooltip": "Any data you wish to iterate on and propagate to subsequent prompts"}),
				"CYCLE": ("CYCLE", {"tooltip": "Connect to the CYCLE output of a [Cycle] node to establish a loop"}),
			}, "optional": {
				"aux_data": (any_type, {"tooltip": "Any optional Auxiliary data you wish to iterate on and propagate to subsequent prompts"}),
				"index_override": ("INT", {"forceInput": True, "tooltip": "Manually override the current index of the Cycle.\nYou can use this input to have complex Step calculations or to reset the loop manually"}),
			}
		}
	  
	RETURN_TYPES = (any_type,any_type,"INT",)
	RETURN_NAMES = ("*","*","index",)
	OUTPUT_TOOLTIPS = ("Connect to the Data input of a [CycleEnd] node after processing","Connect to the Aux_Data input of a [CycleEnd] node after processing","The Index of loop counter before being incremented or decremented by Step",)
	FUNCTION = "run"
	CATEGORY = MAIN_CATEGORY
	DESCRIPTION = \
"""Continues a Cycle, a kind of Loop that gets iterated each time a prompt
is executed. You can use Cycles to send information forwards into subsequent
prompts, allowing for workflows that process data in an iterative manner.

Connect the Data and Aux_Data outputs of this node to a [Cycle End]'s Data
and Aux_Data inputs to continue the loop, ideally after processing them.

The Index output specifies the current value of the loop counter before
Step is applied.

You can connect any outputs to this node's Data or Aux_Data inputs to
propagate that data into subsequent prompt executions. This allows you
to process data iteratively by queuing multiple prompts at a time or even
setting the execution to Instant which will queue up prompts automatically.
Execution can then be interrupted via the [HaltExecution] node on demand
once your Cycle has finished or for any other reason you may have.

HOVER OVER THE INPUTS AND OUTPUTS OF THE NODE FOR MORE INFO.
"""
	
	def run(self, data, CYCLE, aux_data=None,index_override=None):

		if index_override is not None:
				CYCLE['index'] = index_override
		
		if 'index' not in CYCLE:
			raise Exception("CYCLE NOT PROPERLY CLOSED. PLEASE CONNECT THE CYCLE NODES CORRECTLY!")
			return (None,None,None,)
			
		if CYCLE['index'] is None:
		
			debug_print (">> CYCLE START - DRY RUN")
				
			return (None,None,None,)
		
		else:

			if 'next' in CYCLE:
				return (CYCLE['next'],CYCLE['aux'],CYCLE['index'])
			return (data,aux_data,CYCLE['index'])

	@classmethod
	def IS_CHANGED(s, data, CYCLE, aux_data=None):
		if 'next' in CYCLE:
			return id(CYCLE['next'])
		return float("NaN")

class CycleEnd:
	@classmethod
	def INPUT_TYPES(s):
		return {
			"required": {
				"data": (any_type, {"tooltip": "Any data you wish to iterate on and propagate to subsequent prompts"}),
				"CYCLE": ("CYCLE", {"tooltip": "Connect to the CYCLE output of a [Cycle] node to establish a loop"}) 
			}, "optional": { 
				"aux_data": (any_type,{"tooltip": "Any optional Auxiliary data you wish to iterate on and propagate to subsequent prompts"})
			}            
		}
	
	RETURN_TYPES = ("INT","BOOLEAN",)
	RETURN_NAMES = ("index","FINISHED?",)
	OUTPUT_TOOLTIPS = ("The Index of loop counter after being incremented or decremented by Step","Boolean value that specifies whether the cycle has terminated",)
	FUNCTION = "run"
	CATEGORY = MAIN_CATEGORY
	OUTPUT_NODE = True
	DESCRIPTION = \
"""Ends a Cycle, a kind of Loop that gets iterated each time a prompt is
executed. You can use Cycles to send information forwards into subsequent
prompts, allowing for workflows that process data in an iterative manner.

Connect the CYCLE input of this node to a [Cycle]'s CYCLE output node to
establish a loop. Information from Data and Aux_Data will flow through
the CYCLE line and be cached to be retrieved upon the next loop iteration.

The Index output specifies the current value of the loop counter after Step
is applied. The Finished output returns True if the loop counter has reached
or surpassed the value specified by End.

HOVER OVER THE INPUTS AND OUTPUTS OF THE NODE FOR MORE INFO.
"""
	def run(self, data, CYCLE, aux_data=None):
	
		if CYCLE['index'] is None:
			CYCLE['index'] = CYCLE['start']
			
			debug_print (">> CYCLE END - DRY RUN")
			
			return (None,None,None)
		
		debug_print (">> CYCLE ITERATION '", CYCLE['index'],"'!")
		
		CYCLE['next'] = data
		CYCLE['aux'] = aux_data
		CYCLE['index'] += CYCLE['step']
		
		if CYCLE['step'] >= 0:
			CYCLE['finished'] = ( CYCLE['end']+1 - CYCLE['index'] <= 0 )
		else:
			CYCLE['finished'] = ( CYCLE['end']+1 - CYCLE['index'] >= 0)
			
		if CYCLE['finished'] and CYCLE['auto_reset']:
		
			debug_print (">> CYCLE AUTO-RESET!")
		
			CYCLE['index'] = CYCLE['start']
		
		return (CYCLE['index'],CYCLE['finished'])
		
	@classmethod
	def IS_CHANGED(s, data, CYCLE, aux_data=None):
	
		ret = (not CYCLE['finished'])
		
		debug_print ("CYCLE CHANGE:",ret)
		
		return ret
		

class UniversalSwitch: 

	#TODO: Make input and output amounts dynamic and have a working setting for type validation. 
	
	max_slots = 6 #Dynamic adjustment of how many Inputs and Ouputs this node exposes. Change this value to change the corresponding amount.
	default_to_first = True #Constant which determines whether to output on the first slot even if no valid connections are found.
		
	@classmethod
	def INPUT_TYPES(s):
	
		dynamic_inputs = {"input2": (any_type, {"lazy": True}),}
		for x in range(2, s.max_slots+1):
			dynamic_inputs[f"input{x}"] = (any_type, {"lazy": True,"tooltip":"Data to forward through the Universal Switch"})
		return {
			"required": { "input1": (any_type, {"lazy": True,"tooltip": "Data to forward through the Universal Switch"}),
			"mode": (["SWITCH","PASSTHROUGH","CYCLE","SORT","REVERSE"],{"tooltip": "Mode that will be used to select Inputs and Outputs"}),
			"selection_in": ("INT", {"default": 1, "min": -1, "max": s.max_slots, "step": 1, "forceInput": False, "tooltip":"Which Input slot to select from (0=Auto,-1=All)"}),
			"selection_out": ("INT", {"default": 1, "min": -1, "max": s.max_slots, "step": 1, "forceInput": False, "tooltip":"Which Output slot to transmit to (0=Auto,-1=All)"}),
			"validate_typing": ("BOOLEAN", {"forceInput": False,"tooltip":"[UNIMPLEMENTED] Match Input types to their relative Outputs"}), 
			}, "optional": dynamic_inputs, "hidden": {"prompt": "PROMPT", "unique_id": "UNIQUE_ID",}, #"extra_pnginfo": "EXTRA_PNGINFO"},            
		}
		
	#def pack_tuple(s,prefix_type,general_type,count):
		#return tuple([prefix_type] + [general_type for x in range(1,count+1)])
		
	RETURN_TYPES =  tuple([any_type for x in range(1,max_slots+1)])   #pack_tuple(None,"INT",any_type,max_slots) #tuple(["INT"] + [any_type for x in range (1,max_slots+1)])
	RETURN_NAMES = tuple(list("*" * max_slots))    #tuple([x for x in ["Index"] + list( "*" * max_slots) ]) #tuple('*' * max_slots)      #("Index","*","*","*","*","*",)
	OUTPUT_TOOLTIPS = tuple(["Output "+ str(x) for x in range(1,max_slots+1)],) #tuple( ["Index of the Selection that was Chosen (-1 for All)"] + ["Output "+x for x in range(1,s_max.slots)] )
	FUNCTION = "switch"
	CATEGORY = MAIN_CATEGORY
	DESCRIPTION = \
"""Allows you to pick a specific Input or Output to control the flow of execution
and transmit data variably based on your selections.

Selection_In determines what Input slot will be transmited and Selection_Out
specifies what slot that data will be output to. All other Outputs from this
node that are not used will return None. This node supports Lazy evaluation.
Only the Inputs that are required based on the selections will be executed.

Depending on the mode this node is set to, different actions will occur:
• SWITCH: Transmits the Input chosen by Selection_In on the Output of Selection_Out.
• CYCLE: Similar to SWITCH but all subsequent Outputs will be matched linearly
after the chosen Input, wrapping around until all Inputs are matched.
• PASSTHROUGH: All Inputs will be directly matched to all Outputs.
(Selection_in and Selection_Out are ignored).
• SORT: All Inputs will be sorted and matched to all Outputs.
(Selection_in and Selection_Out are ignored).
• REVERSE: All Inputs will be inversely matched to all Outputs.
(Selection_in and Selection_Out are ignored).

If Selection_In is set to 0 (for Modes that support it), the first Input that isn't
None will be selected. Similarly, Selection_Out will pick the first Output slot
that has a valid connection (UNIMPLEMENTED: Currently outputs to 1st slot).

With Selection_In set to -1, all Inputs will be packed into a List and output
through the slot specified by Selection_Out. With Selection_Out set to -1,
the Input chosen by Selection_In will be sent to ALL Outputs simultaneously.
A Selection_In of -1 and a Selection_Out of -1 will match ALL Input Nodes and
ALL Output nodes respectively. With both values set to -1, this is equivalent
to PASSTHROUGH mode.

If Validate_Typing is enabled, Outputs will match the type of their respective Inputs. (Currently this functionality is unimplemented).

HOVER OVER THE INPUTS AND OUTPUTS OF THE NODE FOR MORE INFO.
"""
	def check_lazy_status(s, *args, **kwargs):
	
		selection = int(kwargs['selection_in'])
		
		inputs = []

		if selection > 0 and kwargs['mode'] == "SWITCH":
			inputs = [f"input{selection}"]
		else:
			debug_print ("SWITCH [",kwargs['unique_id'],"] UNABLE TO LAZY CHECK, REQUESTING ALL INPUTS.")
			for x in range(1,s.max_slots+1):
				inputs.append("input"+str(x))

		debug_print ("SWITCH [",kwargs['unique_id'],"] LAZY CHECK REQUESTED: ", inputs)
		
		return inputs
	
	def switch(s,input1,mode,selection_in,selection_out,validate_typing,**kwargs):
	
		#if selection_in is None:
			#return (None*s.max_slots)
	
		def find_valid_output(kwargs):
	
			unique_id,prompt = kwargs.pop('unique_id'),kwargs.pop('prompt') #workflow_info = kwargs.pop('extra_pnginfo')
			val_out = None
			
			debug_print ("\n>> SWITCH [",unique_id,"]: MODE =",mode)
			#debug_print ("\nPROMPT:\n",prompt,"\n") #,"\n\nEXTRA INFO:\n",workflow_info)
			
			for x in range(0,s.max_slots):
				if  "'source': ['"+str(unique_id)+"', " + str(x) + "]" in str(prompt): #str(prompt).find(test_str) != -1:
					val_out = x+1; break
			
			debug_print (">> FIRST VALID OUTPUT SLOT:",val_out)				
			return val_out
			
		selected_slot = None
		valid_out = find_valid_output(kwargs)
		if selection_out == 0: selection_out = valid_out
		
		options = [input1]
		for key,value in kwargs.items(): options.append(value)
		
		debug_print (">> OPTIONS:",options)
		
		if selection_in == 0:
			i=0
			for input in options:
				i+=1
				if input is not None:
					selected_slot = input; selection_in = i
					debug_print (">> SELECTED INPUT SLOT (FIRST VALID):",i)
					break
					
		elif selection_in > 0:     
			if selection_in >= len(options):
				selected_slot = options[len(options)-1]
			else:
				selected_slot = options[selection_in-1]
				
		elif selection_in == -1:
		
			if selection_out == -1:
				mode = "PASSTHROUGH"
			else:
				selected_slot = options
		
		debug_print (">> SELECTED SLOTS -> INPUT:",selection_in," OUTPUT:",selection_out)
		
		match mode:
	
			case "SWITCH":

				if selection_out is None:
					debug_print (">> NO OUTPUTS CONNECTED!")
					ret = [None] * (s.max_slots)
					
					if (s.default_to_first):
						debug_print (">> DEFAULTING TO FIRST OUTPUT SLOT!")
						ret[0] = selected_slot
					
				elif selection_out == -1:
					ret = [selected_slot for x in range(0,s.max_slots)] #s.pack_tuple(selection,selected_slot, s.max_slots)
					
				else:				
					ret = [None] * (s.max_slots) 	#ret = [selection] + [selected_slot] + [None] * (s.max_slots-1)
					ret[selection_out-1] = selected_slot  # ret = s.pack_tuple(-1,input1, s.max_slots)
			
			#The following operation modes are still untested
			
			case "CYCLE":
			
				ret = [None] * (s.max_slots)
				
				for x in range(0,s.max_slots):
				
					i = x+selection_in-1
					debug_print ("I=",i)
					if i > s.max_slots-1:
						i-=s.max_slots
						debug_print ("new I=",i)
				
					j = x+selection_out-1
					debug_print ("J=",j)
					if j > s.max_slots-1:
						j-=s.max_slots
						debug_print ("new J=",j)
					
					#debug_print ("OPTIONS ",i,":",options[i])
					ret[j] = options[i]
					#debug_print ("RET ",j,":",options[j])
				
			case "PASSTHROUGH":
			
				ret = options
				
			case "SORT":
			
				ret = sorted(options)
				
			case "REVERSE":
			
				ret = options[reverse]
			 
		#debug_print("\n>> RETURN: ", ret)
				
		return tuple(ret)
		
	@classmethod
	def IS_CHANGED(s,**kwargs):
		return float("nan")
 
class IfConditionSelector:

	@classmethod
	def INPUT_TYPES(s):
		return {
			  "required": {                             
					"condition": (["A is TRUE", "B is TRUE", "A is NONE","B is NONE", "A == B", "A != B", "A > B", "A >= B", "A < B", "A <= B","A is B","A is not B","A in B", "B in A", "A & B", "A | B", "A ^ B", "CUSTOM"], {"tooltip": "Condition to evaluate. The output will be set to the result."}), 
					"require_inputs": ("BOOLEAN", {"default": True,"label_on":"Return Inputs","label_off":"Return Boolean","tooltip": "Enable to forward TRUE_IN/FALSE_IN Inputs of this node, disable to return Boolean results"}),
					"NOT": ("BOOLEAN",{"tooltip":"Invert the result of the condition post-evaluation"}),
					"custom_expression": ("STRING", {"default": "2*a == 5*b+2","multiline": True, "tooltip": "Custom expression used with the CUSTOM Condition",
					"vykosx.binding": [{
						"source": "condition",
						"callback": [{
							"type": "if",
							"condition": [{
								"left": "$source.value",
								"op": "eq",
								"right": '"CUSTOM"'
							}],
							"true": [{
								"type": "set",
								"target": "$this.disabled",
								"value": False,
							}],
							"false": [{
								"type": "set",
								"target": "$this.disabled",
								"value": True,
							}],
						}]
					}]                    
					}),					
			}, "optional": {
				"A": (any_type, {"forceInput": True, "lazy": True,"tooltip": "First Input to Evaluate"}),
				"B": (any_type, {"forceInput": True, "lazy": True,"tooltip": "Second Input to Evaluate"}),      
				"TRUE_IN": (any_type, {"forceInput": True, "lazy": True, "tooltip": "Input to forward if the expression evaluates to True"}),
				"FALSE_IN": (any_type, {"forceInput": True, "lazy": True, "tooltip": "Input to forward if the expression evaluates to False"}), 
			}, "hidden": { "unique_id": "UNIQUE_ID" } #"comparison_type": (["Values","Length(A)|Value(B)","Length (Both)","Address(A)|Value (B)","Address (Both)"],),
		
	   }
	   
	RETURN_TYPES = (any_type,)
	RETURN_NAMES = ("*",)
	OUTPUT_TOOLTIPS = ("Result of the comparison. Either a forwarded input or a boolean value depending on whether Required_Input is set",)
	FUNCTION = "run_comparison"
	CATEGORY = MAIN_CATEGORY
	DESCRIPTION = \
"""Allows you to test for a condition and change the flow of execution on your prompt based on whether the condition evaluates to TRUE or FALSE.

This node supports Lazy evaluation. Only the Inputs that are required based on the specified condition will be executed.

A and B are the parameters that will be tested against each other and Condition specifies what kind of comparison will be made between them. 

If NOT is enabled then the condition will be reversed after evaluation.

If Require_Inputs is enabled, then you must specify the TRUE_IN and FALSE_IN inputs as their values will be forwarded to the Output based on the results of the evaluation i.e. TRUE_IN will be forwarded if the condition evaluates to TRUE and FALSE_IN will be forwarded if the condition evaluates to FALSE. If Require_Inputs is disabled then TRUE_IN and FALSE_IN can be omitted and the raw boolean values True and False will be returned based on the result of the comparison.

If Condition is set to CUSTOM, you may further specify a custom expression which will be evaluated. Within this expression you may use the variables A and B to refer to
those respective inputs as well as any named global variables from [Memory Storage] nodes. Most valid Python expressions, types and built-in functions are supported in the custom expression. For a full list of supported operations please consult the file 'Helper.py' included in this node pack.

HOVER OVER THE INPUTS AND OUTPUTS OF THE NODE FOR MORE INFO.
"""
	def compare(self,A,B,condition,NOT,custom_expression=""):
	
		global VYKOSX_STORAGE_DATA
	
		ret = False
	
		try:
			match condition:
			
				case "A is TRUE":
					ret = (A == True)
				case "B is TRUE":
					ret = (B == True)
				case "A is NONE":
					ret = (A is None)
				case "B is NONE":
					ret = (B is None)
				case "A is B":
					ret = (A is B)
				case "A is not B":
					ret = (A is not B)
				case "A in B":
					ret = (A in B)
				case "B in A":
					ret = (B in A)
				case "A == B":
					ret = (A == B)
				case "A != B":
					ret = (A != B)
				case "A > B":
					ret = (A > B)
				case "A >= B":
					ret = (A <= B)
				case "A < B":
					ret = (A < B)
				case "A <= B":
					ret = (A < B)
				case "A & B":
					ret = (A & B)
				case "A | B":
					ret = (A | B)
				case "A ^ B":
					ret = (A ^ B)
					
		except Exception as x:
			debug_print ("[!] ERROR PROCESSING CONDITION:",x,". DEFAULTING TO FALSE.")
			pass
			
		if condition == "CUSTOM":
			if custom_expression!="":
			
				Vars = {"A":A,"a":A,"B":B,"b":B} #,"true_in":TRUE_IN,"TRUE_IN":TRUE_IN,"false_in":FALSE_IN,"FALSE_IN":FALSE_IN}
				
				for key, value in VYKOSX_STORAGE_DATA.items():
					Vars[key] = value #replace_caseless('%'+key+'%',value, B)
				
				ret = safe_eval(custom_expression,Vars) #return cbool( ast.literal_eval(B) )

		if NOT:
		
			if type(ret) is bool:            
				ret = not ret            
			else:            
				ret = ~ret
		
		return ret
		
	def check_lazy_status(s,condition,require_inputs,NOT,custom_expression,A=None,B=None,TRUE_IN=None,FALSE_IN=None,unique_id=0):
	
		debug_print (">> IF LAZY CHECK! A:",A,"B:",B,"cond:",condition,"NOT:",NOT,"TRUE:",TRUE_IN,"FALSE:",FALSE_IN)
		
		lazy = []
		
		#if comparison_type != "Values":
			#lazy = ["A","B"]
		#else:
		
		if condition == "CUSTOM":
			if "a" in custom_expression.casefold(): lazy+=["A"]
			if "b" in custom_expression.casefold(): lazy+=["B"]
		else:
			if "A" in condition: lazy+=["A"]
			if "B" in condition: lazy+=["B"]
			
		if require_inputs:
		
			ret = s.compare(A,B,condition,NOT,custom_expression)

			lazy += ["TRUE_IN"] if ret else ["FALSE_IN"]
	
		debug_print (">> LAZY RESULT:",lazy)
		
		return lazy
			
	def run_comparison(s,condition,require_inputs,NOT,custom_expression,A=None,B=None,TRUE_IN=None,FALSE_IN=None,unique_id=0):
   
		debug_print ("\n>> IF CONDITION [",unique_id,"]\n>> COMPARE! A:",A,"B:",B,"cond:",condition,"CUSTOM:",custom_expression,"NOT:",NOT,"TRUE:",TRUE_IN,"FALSE:",FALSE_IN)
	
		ret = s.compare(A,B,condition,NOT,custom_expression)
	   
		debug_print (">> COMPARE RESULT:",ret)
		
		if require_inputs:
			debug_print (">> RETURN:", str(repr(TRUE_IN)).strip("'") if ret else str(repr(FALSE_IN)).strip("'") )
			return (TRUE_IN,) if ret else (FALSE_IN,)
		else:
			debug_print (">> RETURN:",ret)
			return (ret,)

	@classmethod
	def IS_CHANGED(s,**kwargs):
		return float("nan")

class HaltExecution:

	@classmethod
	def INPUT_TYPES(s):
		return {
			"required": {
				"disable": ("BOOLEAN", {"default": False, "forceInput": False, "tooltip": "Will prevent execution from being halted if set to True"}),
				"method":  ("BOOLEAN",{"default": False, "label_off":"Cancel Prompt","label_on":"Block Execution","tooltip":"Method for how to halt the prompt. Cancel Prompt will interrupt the prompt altogether whereas Block Execution will prevent any nodes that follow this one from running."}),
				"clear_queue": ("BOOLEAN", {"default": False, "forceInput": False, "tooltip": "Clear any remaining items in the queue and disable Auto-Queue mode"}),
				"alert_on_trigger": ("BOOLEAN", {"default": False, "forceInput": False, "tooltip": "Raise an alert message when this node interrupts execution"}),
				"input": (any_type,{"tooltip": "Any data you wish to forward through this node"}),
			}, "optional": { "run_after": (any_type, {"tooltip": "Optional input used only to ensure this node will run after any node you connect to this Input"}), 
			}
		}

	RETURN_TYPES = (any_type,)
	RETURN_NAMES = ("*",)
	OUTPUT_TOOLTIPS = ("Will return the same data sent through Input",)
	CATEGORY = MAIN_CATEGORY
	FUNCTION = "halt"
	DESCRIPTION = \
"""Allows you to end the current prompt execution on demand or depending on a given condition.

In order for this node to execute, it must be placed in the middle of an operation, so use the Input and Output channels as a Passthrough for any data you may wish to interrupt from being forwarded. To ensure this node runs at a specific and more predictable order, you may also connect the Output of any node of your choice to the Run_After Input of this node. This node should execute only after the previous node is done executing (lazy execution notwithstanding).

You may convert this node's Disable widget to an Input to make it a Condition that you can trigger with an [IF Selector] Node. If Disable is set to False, the current prompt will be halted prematurely when this node is executed.

Method will determine how the execution will be affected. Cancel Prompt will immediately interrupt execution everywhere when this node runs, whereas Block Execution will allow the execution to continue but will prevent any nodes connected to this one from running subsequently.

The Clear_Queue option will additionally clear your Execution Queue and set your Auto-Queue execution mode to Disabled, allowing you to cancel any pending processes.   

The Alert_On_Trigger toggle will further raise an exception when the node interrupts the flow of execution, ensuring no other cached nodes continue executing after this one, giving you ample time to review your workflow's state after it has been halted.

Run_After is an unused optional parameter made available only to ensure this node executes after the node it is connected to.

HOVER OVER THE INPUTS AND OUTPUTS OF THE NODE FOR MORE INFO.
"""
	def halt(s,disable,method,clear_queue,alert_on_trigger,input,run_after=None):
	
		debug_print (" >> HALT EXECUTION REQUESTED. CANCEL = ", disable)
	
		if not disable and input is not None:
		
			debug_print ("\n"+"-"*36+"\n   # HALTING PROMPT EXECUTION #"+"\n"+"-"*36)           
		
			if clear_queue:
				PromptServer.instance.send_sync("VykosX.ClearQueue", {"interrupt" : not method})
				
			if method:
			
				text = "❌ EXECUTION BLOCKED!"
				
				return {"ui": {"text": text},"result":  (ExecutionBlocker(text if alert_on_trigger else None)),}
				
			else:
			
				nodes.interrupt_processing(True)
				
				text = "🛑 EXECUTION HALTED!"
		
				if alert_on_trigger: raise Exception(text)
				
				return {"ui": {"text": text},"result": (None,)} #return (None,)
				
		text = "➡️ EXECUTION CONTINUING! Time: " + str(datetime.now().time())
		
		return {"ui": {"text": text},"result": (input,)} #return (input,)
		
	@classmethod
	def IS_CHANGED(s,**kwargs):
		return float("nan")
		
class FallbackImagePreviewer(nodes.PreviewImage):

	"""def __init__(self, device="cpu"):
		self.device = device
		self.output_dir = folder_paths.get_output_directory()
		self.type = "output"
		self.prefix_append = ""
		self.compress_level = 4"""

	MAX_RESOLUTION=16384
	
	@classmethod
	def INPUT_TYPES(s):
		return {
			"required": {
				"images": ("IMAGE", {"tooltip": "The images to preview"}),
			}, "optional": {
				"fallback_width": ("INT", {"default": 512, "min": 0, "max": s.MAX_RESOLUTION, "step": 256, "tooltip": "Width of the placeholder image that will be generated if no Images are provided."}),
				"fallback_height": ("INT", {"default": 512, "min": 0, "max": s.MAX_RESOLUTION, "step": 256, "tooltip": "Height of the placeholder image that will be generated if no Images are provided."}),
			}, "hidden": {
			    "prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"
			},
		}

	OUTPUT_NODE = True
	RETURN_TYPES = ()
	FUNCTION = "safe_preview"
	CATEGORY = MAIN_CATEGORY
	DESCRIPTION = """
Allows you to preview an image even when the input is invalid or missing. If the input image is missing a black empty image of dimensions defined by Fallback_Width and Fallback_Height will be generated. If either parameter is set to 0 then no placeholder image will be generated.
"""
	def empty_img_generate(self, width, height, batch_size=1, color=0):
		r = torch.full([batch_size, height, width, 1], ((color >> 16) & 0xFF) / 0xFF)
		g = torch.full([batch_size, height, width, 1], ((color >> 8) & 0xFF) / 0xFF)
		b = torch.full([batch_size, height, width, 1], ((color) & 0xFF) / 0xFF)
		return torch.cat((r, g, b), dim=-1)

	def safe_preview(self, images, fallback_width, fallback_height, prompt, extra_pnginfo):
	
		filename_prefix,results = "VykosX.FallbackPreview", None
		 
		if images is not None:
		
			results = self.save_images (images,filename_prefix,prompt,extra_pnginfo)['ui']['images']
			
		else:
		
			if fallback_width == 0 or fallback_height == 0:
			
				debug_print ( ">> NO VALID IMAGES RECEIVED! IGNORING...")
				return (None,)
			
			else:
		
				debug_print ( ">> NO VALID IMAGES RECEIVED! GENERATING EMPTY IMAGE.")
		
				blank = self.empty_img_generate(fallback_width,fallback_height)
				
				results = self.save_images (blank,filename_prefix,prompt,extra_pnginfo)['ui']['images']
		
		return { "ui": { "images": results } }

class FolderSearch:

	@classmethod
	def INPUT_TYPES(s):
		return {
			"required": {
			   "folder_path": ("STRING", {"default": "/","forceInput": False,"tooltip": "Folder to search for files within"}),
			   "search_mask": ("STRING", {"default": "*.*","forceInput": False,"tooltip": "Pattern to match the found files against"}),
			   "output_type": ("BOOLEAN",{"default": False, "label_on": "Full file list", "label_off": "Current file","tooltip": "How the output should be returned, ALL files or one file at a time"}),
			   "recursive":   ("BOOLEAN",{"default": True,"tooltip": "Specifies whether subfolders should be scanned as well"}),
			   "include_directories": ("BOOLEAN",{"default": False,"tooltip": "Specifies whether directories should be included in the results"}),
			   "return_full_path": ("BOOLEAN",{"default": False,"tooltip": "Specifies whether the full file path should be returned or only the file name and extension"}),
			   "relative_filenames": ("BOOLEAN",{"default": False,"tooltip": "Specifies whether the filenames should be return along with their parent folder, relative to the search directory, or only the filenames themselves.",
			   "vykosx.binding": [{
						"source": "return_full_path",
						"callback": [{
							"type": "if",
							"condition": [{
								"left": "$source.value",
								"op": "eq",
								"right": False
							}],
							"true": [{
								"type": "set",
								"target": "$this.disabled",
								"value": False
							}],
							"false": [{
								"type": "set",
								"target": "$this.disabled",
								"value": True
							}],
						}]
					}]
			   }), 
			}, "optional": {
			   "save_output_to" : ("STRING", {"default": "", "tooltip": "files.txt", "forceInput": False,"tooltip": "Optional output file to save a list of found files to"}),
			},
		}
	
	RETURN_TYPES = (any_type,)
	RETURN_NAMES = ("output",)
	OUTPUT_TOOLTIPS = ("All files found or the current file, based on the Output_Type",)
	FUNCTION = "scan_folder"
	OUTPUT_NODE = True
	CATEGORY = MAIN_CATEGORY
	DESCRIPTION = \
"""Scans a specified folder for files matching a specific pattern.

Set Folder_Path to the absolute or relative (to ComfyUI's root folder) path of the directory you wish to scan.

Set Search_Mask to the pattern you wish to match files to. '*' will match all characters, '?' will match a single character and '#' should match a single numeric character.  Characters within [brackets] must all be matched unless the sequence begins with the '[!brackets]' character, which will exclude those characters instead. You can also specify an entire range to search for such as [a-z].

You may select Output_Type to be either the entire list of files that were found matching the pattern, or only the current file, in which case one file will be returned each time this node is executed, until all files have been processed, at which point the node will return an empty string and reset the search query.

If Recursive is set to True, then subfolders within the main specified directory will also be scanned.

If Return_Full_Path is set to True, found files will be returned with their full qualified path, otherwise only the filename and extension will be returned.

You may optionally point Save_Output_To to a file to save the output of this node to a log file of your choice, which you could then process separately.

HOVER OVER THE INPUTS AND OUTPUTS OF THE NODE FOR MORE INFO.
"""

	SCANNER = None
	OPTIONS = None
	FINISHED = True
	MODE = "w"
	
	def scan_folder(s, **kwargs):
		
		
		debug_print (">> FOLDER SCAN: PATH='",kwargs['folder_path'],"' MASK='",kwargs['search_mask'],"' TYPE=",kwargs['output_type'],"' RECURSIVE='", kwargs['recursive'], "'FULL_PATH=",kwargs['return_full_path'],"' INCLUDE_DIRS= '",kwargs['include_directories'],"' RELATIVE= '",kwargs['relative_filenames'],
		"' SAVE=",kwargs['save_output_to'])

		if (s.FINISHED) or (kwargs != s.OPTIONS):
			
			debug_print (">> FOLDER SCAN RESET!")
			
			s.SCANNER = search_folder (kwargs['folder_path'], kwargs['search_mask'], kwargs['recursive'],kwargs['return_full_path'],kwargs['include_directories'],kwargs['relative_filenames'])
			s.OPTIONS = kwargs
			s.FINISHED = False
			s.MODE = "reset"
			
		if (kwargs['output_type']):
		
		   file = list(s.SCANNER)
		   s.FINISHED = True
		   s.MODE = "w"
		   
		else:
		
			file = next(s.SCANNER, None)
			s.MODE = "w" if s.MODE == "reset" else "a+" 
			
			if file is None:
				debug_print (">> FINAL FILE REACHED!")
				s.FINISHED = True
				return ("",) 

		if kwargs['save_output_to'] != "":

			   
			with open(file, s.MODE , encoding="utf-8") as f:
				
				for line in s.SCANNER:                
					f.write(f"{line}\n")

		return (file,)
		
	@classmethod
	def IS_CHANGED(s, **kwargs):
		return float("nan")
		
		
class DataMonitor:
	
	def __init__(self):
		pass
		
	@classmethod
	def INPUT_TYPES(s):
		return {
			"required": {
			   "text":("STRING", {"default": '',"multiline": True,"forceInput": False,"print_to_screen": True}),
			   "output_type": (["ANY","STRING","INT","FLOAT","BOOLEAN","LIST","TUPLE","DICT","JSON","FORMULA"],{"tooltip":"The type the Passthrough or Text should be converted to"}),
			},
			   "optional": {
				   "passthrough":(any_type, {"default": "","multiline": True,"forceInput": True,"tooltip": "Any value or data to be visualized and forwarded by this node"}),
				   "aux":(any_type, {"default": "","forceInput": True, "tooltip": "Any optional Auxiliary data to be processed by this node"}),                   
			   }, "hidden": { "unique_id": "UNIQUE_ID" }
		}
	
	RETURN_TYPES = (any_type,)
	RETURN_NAMES = ("output",)
	OUTPUT_TOOLTIPS = ("Either Passthrough or Text Data processed by this node",)
	FUNCTION = "data_monitor"
	OUTPUT_NODE = True
	CATEGORY = MAIN_CATEGORY
	DESCRIPTION = \
"""This is a Multipurpose Node that allows you to visualize, generate and manipulate Data from and to any other nodes.

If the Passthrough Input is set, this node's text will be updated to a visual representation of the Data coming through the Input, converted to a string.
The Output node will forward Passthrough following any modifications specified by Output_Type. 

If Passthrough is missing, the text manually entered into the node will be processed and converted to Output_Type. If conversion is not possible an error will be raised.

You can use the Aux Input to further forward Data to be processed by this node, typically in conjunction with the FORMULA Output_Type.

Output_Type can have any of the following values:
• ANY: The Passthrough/Text will be forwarded as is without any modification.
• STRING: The Passthrough/Text will be converted to a String before being forwarded.
• INT: The Passthrough/Text will be converted to an Integer before being forwarded.
• FLOAT: The Passthrough/Text will be converted to a Floating Point Number before being forwarded.
• FLOAT: The Passthrough/Text will be converted to a Boolean (True or False) before being forwarded.
• LIST: The Passthrough/Text will be wrapped or coverted into a List before being forwarded.
• TUPLE: The Passthrough/Text will be wrapped or coverted into a Tuple (a list of constants) before being forwarded.
• DICT: The Passthrough/Text will be converted into a Dictionary before being forwarded. You must specify your expressions in "Key1:Value1,Key2:Value2…" format.
• JSON: The Passthrough/Text will be loaded as a JSON dictionary. It must be valid JSON or the function will fail.
• FORMULA: The Passthrough/Text will be evaluated as Python expression, with full support for most common operators, data types and built-in functions. Internally this is implemented through a restricted subset of the Python language to prevent arbitrary code execution. You can see the full list of support operations and functions in the included 'Helpers.py' file. This output mode allows you to perform complex mathematical and logical operations, including conditionals, loops, lambda functions, list comprehensions, return fully defined arbitrary data types and much, much more.

This node further supports Dynamic Variable Notation which will replace the entries for the following variables:
• %AUX%: Replaces the placeholder %AUX% with the value of the Aux Input (Not Case Sensitive).
• %PREV%: Replaces the placeholder %PREV% with the value of the Last Output emitted by this node (Not Case Sensitive).
• %{VAR_NAME}%: Replaces the placecholder %VAR_NAME% with the value of the Memory Storage associated with that name, e.g. %FileName% (All Memory Storage variables are Case Sensitive).
• %CLEAR%: Completely clears the text and the previous saved value, and returns an empty string (Not Case Sensitive).
• __MEM__STORAGE__GET__: Replaces the placeholder __MEM__STORAGE__GET__ with a dictionary of all currently saved Memory Storage entries and their outputs. You can use this to be able to query and manipulate all saved Memory Storages directly (Case Sensitive).
• __MEM__STORAGE__SET__: Force replaces the internal Memory Storage dictionary with a new dictionary specified by the Aux input, allowing you to overwrite all saved Memory Storages directly. __MEM__STORAGE__SET__ will then be removed from the output after the operation is completed (Case Sensitive).
• __MEM__STORAGE__CLEAR__: Deletes ALL current memory storages from Memory. Equivalent to __MEM__STORAGE__SET__ with an empty dictionary {} in the Auxiliary parameter. Use with caution. (Case Sensitive).
• =>__AUX__DISPLAY__PREFIX__: If this string is found inside the Auxilliary parameter, any text preceding this tag in the Auxilliary parameter will be prepended to the final output of the processing, effectively allowing Aux to be used to display additional information in conjunction with Passthrough.
• __AUX__DISPLAY__SUFFIX__=>: If this string is found inside the Auxilliary parameter, any text following this tag in the Auxilliary parameter will be appended to the final output of the processing, effectively allowing Aux to be used to display additional information in conjunction with Passthrough.

HOVER OVER THE INPUTS AND OUTPUTS OF THE NODE FOR MORE INFO.
"""

	PREVIOUS = ""

	def data_monitor(self,text="",output_type="ANY",passthrough=None,aux=None,unique_id=0):
	
		#TODO:
		#Add $var$ to resolve to the value of mape variables/KJNodes get/set/ and anything everywhere nodes
		
		debug_print("\n>> DATA MONITOR [",unique_id,"]")         
		debug_print("PASSTHROUGH: ", type(passthrough), repr(passthrough) )
		debug_print("AUX: ", type(aux), repr(aux))
		debug_print("OUTPUT TYPE: ", output_type)


		def replace_vars(text_value,aux_value,self):
		
			global VYKOSX_STORAGE_DATA
			
			if text_value is None: text_value = ""
			
			try:
				
				ret = str(text_value)
				
				if aux_value is not None:
					try:
						aux = str(aux_value)
					except:
						aux = ""
				else:
					aux = ""

				if aux.casefold() == "%clear%":
				
					debug_print (">> CLEAR SIGNAL RECEIVED!")
					
					ret,self.PREVIOUS = "",""
				
				else:
				
					debug_print (">> %PREV% =", self.PREVIOUS)
					append_mem = False
					
					if "%prev%" in aux.casefold():
						debug_print (">> %PREV% FOUND IN AUX!")
						aux = replace_caseless(aux,"%prev%", str(repr( self.PREVIOUS)).replace("'",""))
					
					if "%prev%" in ret.casefold():
						debug_print (">> %PREV% FOUND IN TEXT!")
						ret = replace_caseless(ret,"%prev%", str(repr( self.PREVIOUS)).replace("'",""))
						
					if "__MEM__STORAGE__CLEAR__" in ret or "__MEM__STORAGE__CLEAR__" in aux:
						debug_print ("MEM CLEAR REQUEST!")
						ret = ret.replace("__MEM__STORAGE__CLEAR__", "")
						VYKOSX_STORAGE_DATA = {}	
					
					if "__MEM__STORAGE__GET__" in ret:
						ret = ret.replace("__MEM__STORAGE__GET__", str(repr( VYKOSX_STORAGE_DATA)).strip("'\""))
						
					#if "__MEM__STORAGE__GET__" in aux:
						#aux = aux.replace("__MEM__STORAGE__GET__", "")
						#append_mem = True
						
					if "__MEM__STORAGE__SET__" in ret:
					
						if type(aux_value) is dict:
							VYKOSX_STORAGE_DATA = aux_value
							ret = ret.replace("__MEM__STORAGE__SET__", "")
						
						else:
							raise Exception("__MEM__STORAGE__SET__ requires a valid dictionary input in Aux_Input!")
							
					if "__MEM__STORAGE__KEYS__" in ret:
					
						ret = ret.replace("__MEM__STORAGE__KEYS__", ", ".join([k for k in VYKOSX_STORAGE_DATA]) )
						
					if (pos:= aux.find("=>__AUX__DISPLAY__PREFIX__")) > 0:
						ret = aux[:pos]+ret
					
					#pos = -1
					
					if (pos:= aux.find("__AUX__DISPLAY__SUFFIX__=>")) != -1:
						ret+= aux[pos+26:] #26 = len("__AUX__DISPLAY__SUFFIX__=>")
						
					if "%aux%" in ret.casefold():
					
						if aux_value is not None:
					
							debug_print ('REPLACING %AUX% in "'+ret+'" with "'+aux+'"!',end="")
								
							ret = replace_caseless(ret,"%aux%",aux)
							
					if "%" in ret:
					
						l_pos = ret.find("%")
						if l_pos!= -1:
							r_pos = ret.find("%",l_pos+1)
							if r_pos!=-1:
								name = ret[l_pos+1:r_pos]
								if name in VYKOSX_STORAGE_DATA:
									ret = ret.replace("%"+name+"%", str(repr( VYKOSX_STORAGE_DATA[name])).replace("'",""))
				
			except Exception as x:
				raise Exception("AN UNEXPECTED ERROR OCURRED:",x)
				#pass
			
			debug_print (">> PROCESSED TEXT: '",ret,"'",end="")
			
			#if append_mem: ret+= str(repr( VYKOSX_STORAGE_DATA)).strip("'\"")
			self.PREVIOUS = ret
			
			return ret
			
		#else: return text_value
 
		#CHECK HOW DISPLAY ANY RENDERS LATENT IMAGE (if type=dict). Currently crashes.
						
		if (passthrough is not None):                

			encapsulate = False
			
			try:
				iterator = iter(passthrough)
			except TypeError:    
				encapsulate = True
				
				debug_print ("[!] PASSTHROUGH NOT ITERABLE!")                                
			
			else:            
				
				debug_print ("[!] PASSTHROUGH ITERABLE!")
				
				try:
					float(passthrough)                    
				except:
					
					debug_print ("[!] PASSTHROUGH NOT NUMERIC!")                    
				
				else:
					
					debug_print ("[!] PASSTHROUGH NUMERIC!")
					
					encapsulate = True
					
			debug_print("OUTPUT TYPE: ", output_type)

			ret = replace_vars(passthrough,aux,self)

			if ret == "":
			
				return {"ui": {"text": ret}, "result": (ret,)}			
				#return {"ui": {"text": passthrough}, "result": (passthrough,)}
				
			else:
				text = ret
			
			debug_print ( "TEXT:", text )    
			
			match output_type:
				case "INT":
					text = cint(text)
				case "FLOAT":
					text = float(text) 
				case "BOOLEAN":
					text = cbool(text)
					encapsulate=True
				case "STRING":
					text = str(text)
				case "LIST":
					text = list(text) 
				case "TUPLE":
					text = tuple(text)
				case "DICT":
					text = dict(text)
				case "JSON":                         
					text = json.loads(text),                    
				case "FORMULA":
					if text != "":
						text = safe_eval(str(text))
					try:
						float(text)                    
					except ValueError:
						debug_print ("PASSTHROUGH FORMULA NOT NUMERIC!")                    
					else:
						debug_print ("PASSTHROUGH FORMULA NUMERIC!")
						encapsulate = True
				case _:
					text = passthrough
			
			debug_print ("RETURN [PASSTHROUGH]:",type(text), repr(text))
			
			#PromptServer.instance.send_sync("VykosX.UpdateText", {"node_id": unique_id, "msg": text })
			
			display_text = repr(text).strip("'\"") if type(text) is not str else text
			
			if encapsulate:
				return {"ui": {"text": tuple([display_text]) },"result": tuple([text]) }
			else:
				return {"ui": {"text": display_text},"result": (text,)}
		else:

			debug_print("TEXT: ", type(text), repr(text))
			
			text = replace_vars(text,aux,self)

			match output_type:
				case "INT":
					text = cint(text)
				case "FLOAT":
					text = float(text)
				case "BOOLEAN":
					text = cbool(text)
				case "STRING":
					text = str(text)
				case "LIST":
					text = list(text) 
				case "TUPLE":
					text = tuple(text)
				case "JSON":                         
					text = json.loads(text),                    
				case "FORMULA":
					if text != "":
						text = safe_eval(str(text))
			
			debug_print ("RETURN [TEXT]:",text)

			#return {"ui": {"text": str(text)},"result": (text,)}
			
			return (text),

	@classmethod
	def IS_CHANGED(s,**kwargs):
		return float("nan")
		
class CheckpointSelector:
	
	@classmethod
	def INPUT_TYPES(s):
		CHECKPOINT_LIST = sorted(folder_paths.get_filename_list("checkpoints"), key=str.lower)
		return {
			"required": { 
				"checkpoints": (CHECKPOINT_LIST, ),
				#"result": ("BOOLEAN",{"default": False,"label_off": "Selected Checkpoint", "label_on":"ALL Checkpoints","tooltip": "How to return the checkpoints, individually or all of them"})
				}, "optional": {
				"run_after":(any_type, {"default": "","forceInput": True, "tooltip": "Optional input used only to ensure this node will run after any node you connect to this Input"})
				},
			}
			
	RETURN_TYPES = (any_type,)
	RETURN_NAMES = ("Checkpoint",)
	OUTPUT_TOOLTIPS = ("Checkpoint name or list of checkpoints",)    
	FUNCTION = "load_checkpoints"
	CATEGORY = MAIN_CATEGORY
	DESCRIPTION = \
"""This node allows you to query a list of all the Checkpoint models available to ComfyUI.

You can retrieve a single selection, ready to be forwarded into the Loader node of your choice; [CURRENTLY UNIMPLEMENTED] or optionally if Result is enabled, you can obtain a dump of all the available results as a multiline string for further processing.

Run_After is an unused optional parameter made available only to ensure this node executes after the node it is connected to.

HOVER OVER THE INPUTS AND OUTPUTS OF THE NODE FOR MORE INFO.
"""
	def load_checkpoints(self, checkpoints,run_after=None) -> any_type:
		#if result:
			#Implement mechanism for retrieving a list of all available checkpoints
			
		#else:
		return (checkpoints,)
		
class LoraSelector:
	
	@classmethod
	def INPUT_TYPES(s):
		LORA_LIST = sorted(folder_paths.get_filename_list("loras"), key=str.lower)
		return {
			"required": { 
				"lora_name": (LORA_LIST, ),
				#"result": ("BOOLEAN",{"default": False,"label_off": "Selected LoRA", "label_on":"ALL LoRAs","tooltip": "How to return the LoRAs, individually or all of them"})
				}, "optional": {
				"run_after":(any_type, {"default": "","forceInput": True, "tooltip": "Optional input used only to ensure this node will run after any node you connect to this Input"})
				}
			}
			
	RETURN_TYPES = (any_type,)
	RETURN_NAMES = ("LoRA",)
	OUTPUT_TOOLTIPS = ("LoRA name or list of LoRAs",)    
	FUNCTION = "load_lora"
	CATEGORY = MAIN_CATEGORY
	DESCRIPTION = \
"""This node allows you to query a list of all the LoRA models available to ComfyUI.

You can retrieve a single selection, ready to be forwarded into the Loader node of your choice; [CURRENTLY UNIMPLEMENTED] or optionally if Result is enabled, you can obtain a dump of all the available results as a multiline string for further processing. 

Run_After is an unused optional parameter made available only to ensure this node executes after the node it is connected to.

HOVER OVER THE INPUTS AND OUTPUTS OF THE NODE FOR MORE INFO.
"""
	def load_lora(self, lora_name,run_after=None) -> any_type:      
		#if result:
			#return (lora_name.join("\n"),)
		#else:
		return (lora_name,)
		
class VAESelector:
	
	@classmethod
	def INPUT_TYPES(s):
		VAE_LIST = sorted(folder_paths.get_filename_list("vae"), key=str.lower) + ["taesd","taesdxl"]
		return {
			"required": { 
				"vae": (VAE_LIST, ),
				#"result": ("BOOLEAN",{"default": False,"label_off": "Selected VAE", "label_on":"ALL VAEs","tooltip": "How to return the VAEs, individually or all of them"})
				}, "optional": {
				"run_after":(any_type, {"default": "","forceInput": True, "tooltip": "Optional input used only to ensure this node will run AFTER any node you connect to this Input"})
				}
			}
			
	RETURN_TYPES = (any_type,)
	RETURN_NAMES = ("VAE Name",)    
	FUNCTION = "load_vaes"
	OUTPUT_TOOLTIPS = ("VAE name or list of VAEs",)  
	CATEGORY = MAIN_CATEGORY
	DESCRIPTION = \
"""This node allows you to query a list of all the VAEs available to ComfyUI.

You can retrieve a single selection, ready to be forwarded into the Loader node of your choice; [CURRENTLY UNIMPLEMENTED] or optionally if Result is enabled, you can obtain a dump of all the available results as a multiline string for further processing. 

Run_After is an unused optional parameter made available only to ensure this node executes after the node it is connected to.

HOVER OVER THE INPUTS AND OUTPUTS OF THE NODE FOR MORE INFO.
"""
	def load_vaes(self, vae,result,run_after=None) -> any_type:
		#if result:
			#return (vae.join("\n"),)
		#else:
		return (vae,)

class NullInput:
	
	@classmethod
	def INPUT_TYPES(s):      
		return {"required": { "NULL": (any_type, ), }}
	
	@classmethod    
	def IS_CHANGED(s):    
		return True                
		
	RETURN_TYPES = ()    
	CATEGORY = MAIN_CATEGORY
	FUNCTION = "return_null"    
	OUTPUT_NODE = True
	DESCRIPTION = \
"""This node allows you to forward a Null Input (None type) to other nodes, which can sometimes be useful to disregard certain options or to form a connection to a node where you don't actually care about the output. 
"""
	
	def return_null(self,NULL):
		return (None,)

class SimpleToggle:

	@classmethod
	def INPUT_TYPES(s):
		return {
			"required": {
				"toggle": ("BOOLEAN",{"default":True,"label_on":"Enabled","label_off":"Disabled"}),
			}, "optional": {
				"run_after": (any_type,{"tooltip":"Connect something to this slot if you wish to ensure this node runs after another node of your choice"}),
			}
		}
	
	RETURN_TYPES = ("BOOLEAN",)
	RETURN_NAMES = ('out',)
	OUTPUT_NODE = True
	FUNCTION = "return_bool"
	CATEGORY = MAIN_CATEGORY            
	DESCRIPTION = \
"""This is a simple Toggle node that allows you to quickly emit True or False values as inputs for other nodes.
"""
	def return_bool(self,toggle,run_after=None):
		return (toggle,)
		
		
class NullOutput:

	@classmethod
	def INPUT_TYPES(s):
		return {
			"required": {},
		}

	@classmethod
	def VALIDATE_INPUTS(s, **kwargs):
		return True

	
	RETURN_TYPES = (any_type,)
	RETURN_NAMES = ('NULL',)
	OUTPUT_NODE = True
	FUNCTION = "return_null"
	CATEGORY = MAIN_CATEGORY            
	DESCRIPTION = \
"""This node allows you to forward a Null Output (None type) to other nodes, which can sometimes be useful to disregard certain options or to form a connection to a node where an input is mandatory but not actually useful, or simply to be able to compare directly against a None type.
"""

	def return_null(s):
		return (None,)
		
class ImageResolutionAdjust:
	
	@classmethod
	def INPUT_TYPES(s):
	
		MAX_RESOLUTION = 8192
		
		return {"required": { "source_width": ("INT", {"default": 512, "min": 16, "max": MAX_RESOLUTION, "step": 8, "tooltip": "The original width of the image to adjust"}),
							  "source_height": ("INT", {"default": 512, "min": 16, "max": MAX_RESOLUTION, "step": 8, "tooltip": "The original height of the image to adjust"}),
							  "scaling_factor": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 10, "step": 0.1, "tooltip": "The scaling factor to multiply the image's dimensions by. > 1 values affect image width and < 1 values affect image height"}),
							  "target_width": ("INT", {"default": 512, "min": 16, "max": MAX_RESOLUTION, "step": 8, "tooltip": "The new target width of the image where the new height can be automatically extrapolated from"}),
							  "target_height": ("INT", {"default": 512, "min": 16, "max": MAX_RESOLUTION, "step": 8, "tooltip": "The new target height of the image where the new width can be automatically extrapolated from" }),
							  "tolerance": ("INT", {"default": 32, "min": 16, "max": 1024, "tooltip": "How many pixels at most the target width and height should be from each other. Greater values result in greater differences"})
							  }
			   }
	RETURN_TYPES = ("INT","INT","STRING")
	RETURN_NAMES = ("Adj. Width","Adj. Height","Result")    
	OUTPUT_TOOLTIPS = ("Adjusted width of the image after calculation","Adjust height of the image after calculation","String expression that displays the performed calculation",)  
	FUNCTION = "adjust_res"
	CATEGORY = MAIN_CATEGORY
	DESCRIPTION = \
"""This node receives a given image size Source_Width and Source_Height and performs calculations to automatically resize the image based either on a given Scaling_Factor or towards a specific Target_Width and Target_Height.

If the Scaling Factor is used the image's aspect ratio will be adjusted directly. If the value is > 1, the image's width will be multiplied by the Scaling_Factor. If the value is < 1 the image's height will be changed instead.

If either Target_Width and Target_Height (but not both) are specified, the image final size will be adjusted to be rescaled to the target, while still attempting to maintain the closest possible approximation to the original Aspect Ratio. The aggressiveness of this approximation is determined by the value of Tolerance, which will make sure the final sizes are always multiples of Tolerance. If Both are specified (such that they are the same to each other or identical to the Source values), the Adjusted Width and Height will be returned immediately, as no further calculation is required.

For the most part the default values work well, and you should specify either a Target_Width or Target_Height to obtain the desired effect, although Scaling_Factor can also be useful in certain situations. 

HOVER OVER THE INPUTS AND OUTPUTS OF THE NODE FOR MORE INFO.
"""
	
	def adjust_res (self, source_width: int, source_height: int,scaling_factor: float, target_width: int, target_height: int,tolerance:int):
	
		debug_print("W: ",source_width,"H: ",source_height,"DW: ",target_width,"DH: ",target_height,"T: ",tolerance)
	
		new_res = self.calc_imageres(source_width,source_height,scaling_factor,target_width,target_height,tolerance)
		
		match new_res[2]:
			case 0:
				adjust_ret = "TARGET RESOLUTION MAINTAINED."
			case 1:
				adjust_ret = "RESOLUTION ADJUSTED TO FIT ASPECT RATIO."
			case 2:    
				adjust_ret = "RESOLUTION ADJUSTED WITH SCALING FACTOR: " + f'{scaling_factor:.2f}' + "."
		
		return ( new_res[0],new_res[1],"Original Resolution: " + str(source_width) + " x " + str(source_height) + " = "  + f'{source_width*source_height:,}' + ' px. \n' + "Adjusted Resolution: " + str(new_res[0]) + " x " + str(new_res[1]) + " = " + f'{new_res[0] * new_res[1]:,}' + ' px. \n' + adjust_ret ,) 

	def calc_imageres(self, width, height, scaling_factor,target_width,target_height,tolerance=32):

		if (target_width == target_height) or (width != target_width and height != target_height):
			if scaling_factor == 1.0:
			   
				debug_print ("Maintaining Target Resolution")
 
				return (target_width,target_height,0)
			
			else:
				
				debug_print("Resolution Override - Using Scaling Factor")

		w_diff,h_diff = 1,1

		debug_print("Src W: ", width,"Src H:",height,"Target W:",target_width,"Target H:",target_height)
		debug_print("Src S: ", width*height,"Target S:",target_width*target_height)
		debug_print("W diff: ", w_diff,"H diff: ",h_diff)
			
		if scaling_factor == 1:
			w_diff = width / target_width
			h_diff = target_height / height            
		else:        
			w_diff,h_diff = 1/scaling_factor,1/scaling_factor

		debug_print("W diff: ", w_diff,"H diff: ",h_diff)
		
		if h_diff != 1:
			
			debug_print(">> Adjusted Width")
			target_width = self.round_to_multiple (target_width/h_diff,tolerance)
		  
		if w_diff != 1:
			
			debug_print(">> Adjusted Height")
			target_height = self.round_to_multiple (target_height*w_diff,tolerance)

		debug_print("New W:",target_width,"New H:",target_height,"New S:",target_width*target_height)
		
		return (target_width,target_height, 1 if scaling_factor==1 else 2)
	
	def round_to_multiple(self, number, multiple, direction='nearest'):
		if direction == 'nearest':
			return multiple * round(number / multiple)
		elif direction == 'up':
			return multiple * ceil(number / multiple)
		elif direction == 'down':
			return multiple * floor(number / multiple)
		else:
			return multiple * round(number / multiple)
			
class ReadTextFile():

	#Line (-1 = all file, 0 = next line), return line count, loop on each line

	@classmethod
	def IS_CHANGED(self, **kwargs):
		return os.path.getmtime(kwargs['file'])
		
	@classmethod
	def INPUT_TYPES(s):
		return {
			"required": {
				"file": ("STRING", {"default": "file.txt","tooltip":"Absolute or relative path of the file to read"}) 
			}, "optional": {            
				"line": ( "INT", { "default": 0, "forceInput": False,"tooltip":"Line number to read within the file or '0' to read the whole file at once"}),
				"on_eof": ( "BOOLEAN", {"default": True, "label_on": "Ignore","label_off":"Raise Error","forceInput": False,"tooltip":"Action to perform if the specified line number does not exist"}),
			}
		}

	FUNCTION = "load_text"
	RETURN_TYPES = ("STRING",)
	CATEGORY = MAIN_CATEGORY
	OUTPUT_TOOLTIPS = ("Full contents of the text file or the line of your choice",)
	DESCRIPTION = \
"""This node receives a file path and reads the contents of the file into a string buffer in the UTF-8 format and returns the data read.

If a given Line number is specified, only that line will be returned. If Line is 0, the entire file will be read as plaintext and returned.

If On_EOF is set to Ignore, Line numbers larger than exist within the file will be silently ignored and the node will return an empty string. Otherwise an error will be raised to alert the user.

HOVER OVER THE INPUTS AND OUTPUTS OF THE NODE FOR MORE INFO.
"""
	
	def load_text(self, file,line=0,on_eof=True):
	
		result = ""
		
		if file is not None:

			if os.path.isfile(file):

				with open(file, "r", encoding="utf-8") as f:
					
					try:
						if line==0:
							result = (f.read(), )
						else:
							lines=f.readlines()
							if on_eof:
								result = [line-1] if line <= len(lines) else line[-1]
							else:
								result = [line-1] if line <= len(lines) else ""
					except:
						pass
					
		return (result,)

class SaveTextFile():
	
	@classmethod
	def IS_CHANGED(self, **kwargs):
		return float("nan")
		
	@classmethod
	def INPUT_TYPES(s):
		return {
			"required": {                
				"file_path": ("STRING", {"default": "out.txt","tooltip": "Absolute or relative path of the file to write to"}),
				"mode": (["append", "overwrite", "new only"], {"tooltip": "Mode that the file should be written as" }),
				"terminator": ("BOOLEAN", {
					"default": True, "label_on": "new line", "label_off": "none", "tooltip": "Whether to include a new line after appending to the file",
					"vykosx.binding": [{
						"source": "mode",
						"callback": [{
							"type": "if",
							"condition": [{
								"left": "$source.value",
								"op": "eq",
								"right": '"append"'
							}],
							"true": [{
								"type": "set",
								"target": "$this.disabled",
								"value": False
							}],
							"false": [{
								"type": "set",
								"target": "$this.disabled",
								"value": True
							}],
						}]
					}]
				}),
				"text": ("STRING", {"multiline": True,"tooltip": "Text to write to the file. Right Click and convert to input to specify dynamicaly"})
			},
		}
	
	RETURN_TYPES = ("BOOLEAN",)
	RETURN_NAMES = ("SUCCESS?",)
	OUTPUT_TOOLTIPS = ("Returns True if the file was successfully written to, False otherwise",)
	CATEGORY = MAIN_CATEGORY
	OUTPUT_NODE = True
	FUNCTION = "write_text"
	DESCRIPTION = \
"""This node receives a file path and writes the contents of Text to the file in question, in UTF-8 plaintext format. The result of the operation is then returned by the Boolean Output SUCCESS?.

Depending on the writing Mode of your choice, the file may be either Appended to (new lines will be added to the end of the file without changing the original content), Overwritten (the file will be removed and replaced with the contents of Text) or if Mode is set to New Only, the operation will fail if the file already exists and its contents will remain unchanged.

Additionally, if the Mode is set to Append you may choose whether or not to add a New Line terminator at the end of the file, so that any subsequent writes start in a new line rather than being written contiguously.

To specify a dynamic Text, convert the Text widget of this node to an input.

HOVER OVER THE INPUTS AND OUTPUTS OF THE NODE FOR MORE INFO.
"""
	def write_text(self, file_path, mode, terminator, text):
	
		if file_path != "":
	
			if mode == "new only" and os.path.exists(file_path):
				raise Exception("File already exists and 'new only' is selected.")
				Return (False,)
			   
			with open(file_path, "a+" if mode == "append" else "w", encoding="utf-8") as f:
			
				is_append = f.tell() != 0
				
				if is_append and terminator:
					f.write("\n")
					
				f.write(text)
				
				return (True,)

		return (False,)

class StringOperation:

	@classmethod
	def INPUT_TYPES(s):
	  return {
		"required": {			  
			  "input": (any_type, { "forceInput": True , "tooltip": "Input String or List to process"} ),              
			  "operation": (['COMPARE', 'CONCATENATE', 'COUNT', 'ENDS_WITH', 'EXTRACT_BETWEEN', 'FIND', 'GENERATE', 'GET_LINE', 'IS_ALPHA', 'IS_NUMERIC', 'JOIN', 'LENGTH', 'LOWERCASE', 'PROPERCASE', 'REPLACE','RANDOM_INPUT','RANDOM_ELEMENT', 'REVERSE', 'SLICE', 'SPLIT', 'SPLIT_LINES', 'STARTS_WITH', 'STRIP','TO_LIST','TO_STRING', 'TRIM_SPACES', 'UPPERCASE'],
			  {"tooltip": "Operation to perform on the Input"}),
			  "start_from_end": ("BOOLEAN",{"tooltip": "Whether to evaluate from the start or the end of the expression"}),
			  "case_insensitive": ("BOOLEAN",{"tooltip":"Ignore case sensitivity for operations that support it"}),
		}, "optional": {
			  "aux1": (any_type, { "forceInput": True, "tooltip": "Auxiliary Input 1 (Purpose varies based on operation)"} ),
			  "aux2": (any_type, { "forceInput": True, "tooltip": "Auxiliary Input 2 (Purpose varies based on operation)"} ),
			  "aux3": (any_type, { "forceInput": True, "tooltip": "Auxiliary Input 3 (Purpose varies based on operation)"} ),
			  "param1": ("STRING", { "forceInput": False, "tooltip": "Will be used instead of Aux1 if not empty (Purpose varies based on operation)"} ),
			  "param2": ("STRING", { "forceInput": False, "tooltip": "Will be used instead of Aux2 if not empty (Purpose varies based on operation)"} ),
			  "param3": ("STRING", { "forceInput": False, "tooltip": "Will be used instead of Aux3 if not empty (Purpose varies based on operation)"} ),
		}, "hidden": { "unique_id": "UNIQUE_ID" }
	  }

	RETURN_TYPES = (any_type,any_type,)
	RETURN_NAMES = ("output","result",)
	OUTPUT_TOOLTIPS = ("The Input value after being processed by the chosen operation","Result of the chosen operation",)
	FUNCTION = "process"
	CATEGORY = MAIN_CATEGORY
	DESCRIPTION = \
"""This node allows you to perform many different types of String and List manipulations based on the selected Operation and the values of its Input and Auxiliary Inputs. You can chain multiples of this node to perform very complex operations or even process data condtionally with the help of [If Selector] and [Universal Switch] nodes.

For most operations, the Result output will specifiy either its success or return any relevant indexes. Whereas Output will remain unchanged or will be modified to suit the operation. If Start_From_End is chosen, this will begin the operation from the end of the string instead of the beginning or from the last element of a list rather than the first. For operations that are typically case sensitive, you can force them to ignore case sensitivity by enabling Case_Insensitive.

For most operations, auxiliary values will be required. These may be supplied either through the Aux1 to Aux3 slots which accept arguments of any type, or through the built-in Param1 to Param3 string inputs. The latter will be prioritized for convenience if they are not left empty. For more advanced operations that require parameters that are not strings, please use the Aux Input slots directly.
 
The following operations are available, with their respective required and optional arguments. Optional arguments are denoted within [brackets]:

• COMPARE: Compares the values of a String or List specified by Input to the values specified by any of the Auxiliary inputs. The Result will be a binary sum of how many of the Auxiliary Inputs match Input. For instance, if only Aux1 matches Input, the Result will be 1, If only Aux2 matches Input the result will be 2. If they both match the result will be 3. And if all Aux inputs match the result will be 7. If no matches occur the result will be 0. For strings, the comparison is the same between Input and all Aux Inputs, but for Lists, The elements will be matched in order, such that Aux1 will be compared to Input[0],Aux2 will be compared to Input[1] and Aux3 will be compared to Input[2]. If Start_From_End is enabled, the comparisons will be done in reverse order. 
⸨ Input:String/List = Original expression compare, Aux1,[Aux2,Aux3]:String/List = Expressions to compare against. ⸩

• CONCATENATE: Appends one or multiple Strings or Lists to each other. If Start_From_End is enabled, the values will be prepended to the beginning of the Input rather than appended to the end.
⸨ Input:String/List = Expression to append to, [Aux1,Aux2,Aux3:String/List] = Other expressions to append. ⸩

• COUNT: Returns the number of times that a given expression occurs within a source expression. The number of times the substring is found within Input will be returned in Result and Output will be unchanged. Start_From_End has no effect.
⸨ Input: String/List = Expression to process, Aux1:String = Substring to search for. ⸩

• ENDS_WITH: Tests if a given String or List ends with the specified substring. The result of the operation will be returned in Result and Output will be unchanged. Start_From_End will reverse the list or string prior to checking. For Lists only the first or last element will be checked depending on Start_From_End.
⸨ Input:String/List = Expression to process, Aux1:String = Substring to search for. ⸩

• EXTRACT_BETWEEN: Returns a List of extracted substrings found within a source String or List that match a given pattern. You can use this operation to extract values within delimiters of your choice. E.g. "This %is$ a %test$!" will return a List containing ["is","test"]. The delimiters to check for may be the same or different. Output will be the List of substrings found or an empty list if there were no matches. Result will be the number of tokens extracted.
⸨ Input:String/List = Expression to search for tokens to extract. Aux1:String = Preffix Delimiter, [Aux2:String] = Suffix delimiter. If Aux2 is omitted, it will be treated as the same as Aux1. ⸩

• FIND: Attempts to locate a given substring within an Input List or String. If Input is a list, the Result will be a list with the first occurrence of the substring in each element. If the Input is a string, the Result will be an integer with the index of the first ocurrence of the substring. If the substring is not found, this integer will be -1 instead of the index at which the substring occurs. You can further tune the specifics of the operation with the Aux2 and Aux3 optional parameters to restrict matches only to given portion of the Input. Output is not changed by this operation. If Start_From_End is specified, the operation will instead look for the last occurence of the substring.
⸨ Input:String/List = Expression to process, Aux1:String = Substring to find, [Aux2:Int] = Initial Position to search, [Aux3:Int] = Final Position to search. ⸩

• GENERATE: Repeats a given string a specified number times, optionally separated with a delimiter of your choice. Output is a string repeated a given number of times. Result will be the True if operation succeeds and False otherwise.
⸨ Input:String = Base expression to generate, Aux1:Int = Number of times to repeat, Aux2:String = Optional Delimiter that will be inserted for each repetition. ⸩

• GET_LINE: Retrieves a specific line from a String or a specific element from a List. Output will be the line or element chosen, or an empty string if the operation fails. Result will be the True if operation succeeds and False otherwise. If Start_From_End is specified, the expression will be parsed in reverse order.
⸨ Input:String/List = Expression to parse. Aux1:Int = Line Number or Index of a list element to retrieve. ⸩

• IS_ALPHA: Tests whether an expression contains exclusively alphabetical characters. Result will be True if the operation succeed, False otherwise. Output will not be changed.
⸨ Input:String/List = Expression to parse. ⸩

• IS_NUMERIC: Tests whether an expression is numeric and can be successfully typecast to a FLOAT. Result will be True if the operation succeed, False otherwise. Output will not be changed.
⸨ Input:String/List = Expression to parse. ⸩

• JOIN: Joins a List into a String, optionally separated by the delimiter of your choice. Result will be True if the operation succeed, False otherwise. If Start_From_End is set, the list will be joined in reverse order of the elements. Output is a string with the joined elements.
⸨ Input:List = List to join. Aux1:String = Optional delimiter to separate each element⸩

• LENGTH: Returns the length of a string or the number of elements in a List. Result will be set to the length of the expression. Ouput will not be changed. Start_From_End has no effect.
⸨ Input:String/List = Expression to evaluate. ⸩

• LOWERCASE: Converts an expression to lowercase. For lists, all elements will be converted. Result will be True if the operation succeed, False otherwise. Output is a converted expression.
⸨ Input:String/List = Expression to evaluate. ⸩

• PROPERCASE: Converts an expression to Propercase (the first letter of each sentence will be capitalized). For lists, all elements will be converted. Result will be True if the operation succeed, False otherwise. Output is a converted expression.
⸨ Input:String/List = Expression to evaluate. ⸩

• RANDOM_INPUT: Returns one of the inputs (Input,Aux1,Aux2,Aux3) of the node at random. If the Input is missing it will not be considered.
⸨ Input:Any = Input to randomly choose from. [Aux1,Aux2,Aux3:Any] = Optional inputs to randomly choose from. ⸩

• RANDOM_ELEMENT: Returns an element from an Input list at random. If Aux1 is True then the element will be removed from the source list after being returned.
⸨ Input:List = List to choose an element at random from. [Aux1:Boolean] = Whether to pop the item from the list or simply return it. ⸩

• REPLACE: Replaces any ocurrences of a given substring within an Input List or String. For Lists, each element will be evaluated separately. Result will be True if the operation succeed, False otherwise. Output will be in the same form as Input, after the replacements have been made.
⸨ Input:String/List = Expression to evaluate. Aux1:String = Substring to search for. Aux2:String = Expression to replace the substring with. [Aux3] = Maximum number of replacements for each element. ⸩

• SLICE: Outputs a subsection of the Input according to the given parameters. Negative values are also possible for the Auxiliary inputs. This uses Python's slice notation, consult the Python slicing documentation if in doubt. Result will be the length of the sliced expression. 
⸨ Input:String/List. [Aux1:Int] = First element/character to slice from. [Aux2:Int] = Final element/character to slice to. [Aux3] = Step to skip for each iteration. ⸩

• SPLIT: Outputs a list from a String divided by the delimiter of your choice. Opposite of Join. Result will be the length of the Output list. 
⸨ Input:String = Expression to split, Aux1:String = Delimiter to split the string by, [Aux2:Int] = Maximum amount of splits before the remainder of the string is returned untouched. ⸩

• SPLIT_LINES: Outputs a List with all the separate lines of a given String. Result will be the length of the Output list. 
⸨ Input:String = Expression to split. ⸩

• STARTS_WITH: Tests if a given string or list starts with the specified substring. The result of the operation will be returned in Result and Output will be unchanged. Start_From_End will reverse the list or string prior to checking. For Lists only the first or last element will be checked depending on Start_From_End.
⸨ Input:String/List = Expression to process, Aux1:String = Substring to search for. ⸩

• STRIP: Removes a given set of characters from the beginning and end of a string. Result will be the length of the new expression after stripping. The output will be the stripped string. Start_From_End has no effect on this operation.
⸨ Input:String = Expression to process, Aux1:String = Characters to remove. ⸩

• TO_LIST: Attempts to convert the Input to a List. If the Input is already a list, no changes are made. Result will be True if the operation succeed, False otherwise. If Start_From_End is set the output will be reversed.
⸨ Input:Any = Expression to convert to List. ⸩

• TO_STRING: Attempts to convert the Input to a string. Raises an error if not successful. Result will be True if the operation succeed, False otherwise. If Start_From_End is set the output will be reversed.
⸨ Input:Any = Expression to convert to String. ⸩

• TRIM_SPACES: Removes spaces from the beginning and end of an expression. Result will be the length of the new expression after trimming. 
⸨ Input:Any = Expression to remove prefix and suffix spaces from. ⸩

• UPPERCASE: Converts an expression to UPPERCASE. For lists, all elements will be converted. Result will be True if the operation succeed, False otherwise. Output is a converted expression.
⸨ Input:String/List = Expression to evaluate. ⸩
"""
	
	
	CASE_INSENSITIVE = False
	
	def case(s,expr):
	
		return expr if not s.CASE_INSENSITIVE else expr.casefold()
	
	def process(s,input,operation,start_from_end,case_insensitive,aux1=None,aux2=None,aux3=None,param1="",param2="",param3="",unique_id=0):
	
		debug_print(">> STRING/LIST OP [",unique_id,"] OPERATION=",operation,"START_FROM_END=",start_from_end,"CASE_INSENSITIVE=",case_insensitive,"INPUT=",str(repr(input)),"AUX1=",str(repr(aux1)),"AUX2=",str(repr(aux2)),"AUX3=",str(repr(aux3)),"PARAM1=",param1,"PARAM2=",param2,"PARAM3=",param3)
	
		Fail = False
		result = None
		s.CASE_INSENSITIVE = case_insensitive
		
		try:
			expr = str(input) if not start_from_end else str(input[reverse])
		except:
			raise Exception("Input cannot be successfully converted to a string!")
			return ("",None)
			
		if param1 != "": aux1=param1
		if param2 != "": aux2=param2
		if param3 != "": aux3=param3
		
		match operation:
		
			case 'RANDOM_INPUT':
			
				tmp = [input]
				if aux1 is not None: tmp.append(aux1)
				if aux2 is not None: tmp.append(aux2)
				if aux3 is not None: tmp.append(aux3)
				
				result = rnd(0,len(tmp))
				expr = tmp[result]
				start_from_end = False
				
			case 'RANDOM_ELEMENT':
			
				if not is_list(Input):
					raise Exception("The RANDOM_ELEMENT operation expects a List for Input!")
					result = -1
					expr = []
				else:
					result = rnd(0,len(Input))
					if aux1 is not None and cbool(aux1):
						expr = Input.pop(result)
					else:
						expr = Input[result]
				start_from_end = False
				
			case "CONCATENATE": #Input,Aux1-3 = String or Lists to concatenate

				tmp = [] if is_list(input) else ""

				for x in [aux1,aux2,aux3]:
				
					if x is not None: tmp+=x
					
				expr = input+tmp if not start_from_end else tmp+input		
				start_from_end = False
							
			case "JOIN": #Input = List of strings to join, Aux1 = Optional Delimiter 
			
				if aux1 is None:
					aux1=""
				
				if start_from_end:
					input = input[reverse]
					start_from_end = False
				
				try:
					expr = aux1.join(input)
					result = True
				except:
					Fail = True
					
			case "GENERATE": #Input = Base string, aux1 = Times to repeat, aux2 = Optional Delimiter
				
				try:				
					
					i = cint(aux1)
					
					if i > 0:
					
						if is_list(input):
							tmp = []
							if start_from_end:
								input = input[reverse]
								start_from_end = False
						else:
							tmp = ""
						
						for x in range (1,i+1):
							
							if is_list(input):
								tmp += input
								if type(aux2) is str and x!=i:
									if aux2!="": tmp += [aux2]
							else:
								tmp += expr
								if type(aux2) is str and x!=i: tmp += aux2
								
						expr = tmp
						result = True
								
					else: raise
					
				except:
					result = False
					raise Exception("Aux1 must be a positive number for the GENERATE operation!")
			
			case "LENGTH": #Input = String or List
			
				result = len(input)
			
			case "COUNT": #Input = String or List, Aux1=Expression to count
				
				try:                
					result = input.count(aux1)
				except:
					Fail = True
					
			case "STARTS_WITH": #Input = String or List, Aux1=Expression to check
			
				aux1 = str(aux1)
			
				if is_list(input):
				
					try:
					
						tmp = str(input[-1]) if start_from_end else str(input[0])
					
						result = s.case(tmp).startswith(s.case(aux1))
						
						expr = input; start_from_end = False
						
					except:
						Fail = True
				else:
		
					try:
						aux1 = str(aux1[reverse]) if start_from_end else str(aux1)
						result = s.case(expr).startswith(s.case(aux1))
					except:
						Fail = True
						
			case "ENDS_WITH": #Input = String or List, Aux1=expression to check
			
				aux1 = str(aux1)
			
				if is_list(input):
				
					try:
					
						tmp = str(input[-1]) if start_from_end else str(input[0])
					
						result = s.case(tmp).endswith(s.case(aux1))
						
						expr = input; start_from_end = False
						
					except:
						Fail = True
				else:
		
					try:
						aux1 = str(aux1[reverse]) if start_from_end else str(aux1)
						result = s.case(expr).endswith(s.case(aux1))
					except:
						Fail = True
			
			case "TO_LIST": #Expr is already str(input) or the operation failed
			
				if start_from_end: input = input[reverse]
				
				if is_list(input):
					expr = input
				else:
					expr = list(input)
					
				result = True
				start_from_end = False
				
			case "TO_STRING": #Expr is already str(input) or the operation failed
			
				result = True
				start_from_end = False
				
			case "IS_NUMERIC": #Input = String or List
			
				expr = input[reverse] if start_from_end else input
				result = word_test("numeric",expr)
				start_from_end  = False
						
			case "IS_ALPHA": #Input = String or List
				
				expr = input[reverse] if start_from_end else input
				result = word_test("alpha",expr)
				start_from_end = False
				
			case "GET_LINE": #Input = String or List, aux1= Line number/List index
				
				i = cint(aux1)
			
				if is_list(input):
				
					try:
						expr = str(input[i]) if not start_from_end else str(input[-i])
						result = True
						start_from_end = False
					except:
						expr = ""; result = False
				else:
				
					if i > 0:
						try:
							expr = expr.splitlines()[i-1]
							result = True
						except:
							expr = ""; result = False
					else:
					
						raise Exception("Aux1 must be a positive number for the GET_LINE operation!")
					
			case "STRIP" | "TRIM_SPACES": #Input = String or List, Aux1=chars to strip
			
				try:
					if operation != "STRIP":
						aux1 = " "
					else:
						aux1 = str(aux1)
				
					if not is_list(input): 
						tmp = [expr]
					else:
						tmp = input if not start_from_end else input[reverse]
						start_from_end = False
					
					for x in range(0,len(tmp)):
					
						tmp[x] = tmp[x].strip(aux1)
						
						if case_insensitive:
							tmp[x] = tmp[x].strip((aux1).casefold())
							tmp[x] = tmp[x].strip((aux1).upper())
							
					expr = tmp if is_list(input) else tmp[0]
					result = len(expr)
					
				except:
				
					Fail = True
				
			case "REPLACE": #Input = String or List, Aux1=Replace,Aux2=ReplaceWith,Aux3=MaxReplacements
							   
				if aux3 is None:
					i = -1
				else:
					i = cint(aux3)
					if i == 0: i = -1
				
				if is_list(input):
				
					tmp,ret = [],""

					for x in range(0,len( input )):
					
						ret = str(input[x])
						
						if case_insensitive:
							ret = replace_caseless(ret[reverse] if start_from_end else ret, aux1,aux2, i)
						else:
							ret = ret[reverse] if start_from_end else ret
							ret = ret.replace(aux1,aux2,i)
							
						tmp.append (ret[reverse] if start_from_end else ret)
						
					expr = tmp; start_from_end = False
					result = True
					
				else:
									
					expr = replace_caseless(expr,aux1,aux2,i) if case_insensitive else expr.replace(aux1,aux2,i)
					result = True
			
			case "REVERSE": #Input = String or List
			
				if is_list(input):
					expr = list(input[reverse])
				else:
					expr = str(input[reverse])
					
			case "SLICE": #Input = String or List,Aux1=Start,Aux2=End,Aux3=Step
				
				if aux1 is not None:
					aux1 = cint(aux1)
				
				if aux2 is not None:
					aux2 = cint(aux2)
					
				if aux3 is not None:
					aux3 = cint(aux3)
				
				if start_from_end:
					input = input[reverse]
				
				expr = input[aux1:aux2:aux3]
				result = len(expr)
				
			case "FIND": #Input String or List,Aux1 = Expression to Find,Aux2 = Initial Position,Aux3 = End Position
			
				try: #aux1 = str(aux1[reverse]) if start_from_end else str(aux1)
					aux1 = str(aux1)
					
					if aux2 is not None:
						aux2 = cint(aux2)
					
					if aux3 is not None:
						aux3 = cint(aux3)
				   
					if is_list(input):
					
						tmp = []
					   
						if start_from_end:
							input = input[reverse]
						
						for x in input:
							tmp.append ( s.case(x).find(s.case(aux1),aux2,aux3) )
							#if result != -1: break
						
						result = tmp[0] if len(tmp) == 1 else tmp
						expr = input
						
					else:
					
						if start_from_end:
							result = s.case(str(input)).rfind(s.case(aux1),aux2,aux3)
						else:
							result = s.case(expr).find(s.case(aux1),aux2,aux3)
						
				except:
					Fail = True
			   
			
			case "EXTRACT_BETWEEN": #Input String // or List, Aux1=Prefix Delimiter,Aux2=Suffix Delimiter
		   
				tmp = []
				
				try:
					aux1 = s.case(str(aux1))
					expr = str(input)
					
					if aux2 is not None:
						try:
							aux2 = s.case(str(aux2))
							tmp = extract_between(expr,aux1,aux2)
						except:
							Fail = True
					else:
						tmp = extract_between(expr,aux1)
				except:
					Fail = True
					
				if len(tmp) == 0:
					expr,result = "",0
		
				else:
				
					expr,result = tmp,len(tmp)
					
					if start_from_end: 
						expr=expr[reverse]; start_from_end = False
					
			case "COMPARE": #Input = String or List, Auxs=Strings or Lists to compare
			
				result = 0
				
				if is_list(input):
				
					if is_list(aux1):
						aux1 = str(aux1[0]) if not start_from_end else str(aux1[-1])
						tmp = str(input[0]) if not start_from_end else str(input[-1])
						if (s.case(tmp) == s.case(aux1)): result+=1
					else:
						if (s.case(expr) == s.case(str(aux1))): result+=1
						
					if aux2 is not None and is_list(aux2):
						aux2 = str(aux2[0]) if not start_from_end else str(aux2[-1])
						tmp = str(input[1]) if not start_from_end else str(input[-2]) 
						if (s.case(tmp) == s.case(aux2)): result+=2
					else:
						if (s.case(expr) == s.case(str(aux1))): result+=2
						
					if aux3 is not None and is_list(aux3):
						aux3 = str(aux3[0]) if not start_from_end else str(aux3[-1])
						tmp = str(input[2]) if not start_from_end else str(input[-3]) 
						if (s.case(tmp) == s.case(aux3)): result+=4
					else:
						if (s.case(expr) == s.case(str(aux3))): result+=4	
						
					expr = input
					start_from_end = False
						
				else:
		
					aux1 = str(aux1[reverse]) if start_from_end else str(aux1)
					if (s.case(expr) == s.case(aux1)): result+=1
					
					if aux2 is not None:
						aux2 = str(aux2[reverse]) if start_from_end else str(aux2)
						if (s.case(expr) == s.case(aux2)): result+=2
						
					if aux3 is not None:
						aux3 = str(aux3[reverse]) if start_from_end else str(aux3)
						if (s.case(expr) == s.case(aux3)): result+=4
					
			case "UPPERCASE": #Input = String or List

				try:
					expr = expr.upper()
					result = True
				except:
					Fail = True
					
			case "LOWERCASE": #Input = String or List
			
				try:
					expr = expr.casefold()
					result = True
				except:
					Fail = True
					
			case "PROPERCASE": #Input = String or List
			
				if is_list(input):
				
					for x in range(0,len(input)):
						
						try:
							input[x] = input[x].capitalize()
						except:
							Fail = True
							break
							
					expr = input; start_from_end = false
					result = True
					
				else:

					expr = expr.capitalize()
				
			case "SPLIT": #Input = String, aux1 = delimiter, aux2 = max 
			
				if is_list(input):
				
					expr = input
					raise Exception("The input cannot be a List for the SPLIT operation!")
					
				else:
				
					aux1 = s.case(str(aux1[reverse])) if start_from_end else s.case(str(aux1))
					
					aux2 = cint(aux2) if aux2 is not None else -1
					
					expr = str(expr).split(aux1,-1 if aux2 == 0 else aux2)
					result = len(expr)
				
			case "SPLIT_LINES": #Input = String
			
				if is_list(input):
				
					expr = input
					raise Exception("The input cannot be a List for the SPLIT_LINES operation!")
				
				else:
				
					expr = str(expr).splitlines();	result = len(expr)
				
		if Fail:
		
			result = False
			raise Exception("One of the inputs cannot be successfully converted to a string!")
		
		if start_from_end:
			
			expr = [x[reverse] for x in expr] if is_list(expr) else expr[reverse]
		
		return (expr,result,)
					   
class MemoryStorage:
	
	@classmethod
	def INPUT_TYPES(s):
	  return {
		"required": {			  
			  "Name": ("STRING", { "forceInput": False,"tooltip": "Unique and case-sensitive identifier for the Memory Storage"} ),
		}, "optional": {
			  "Input": (any_type, { "forceInput": True,"tooltip": "Value to set the Memory Storage to, and to passthrough" } ),
			  "Reset": ("BOOLEAN", { "forceInput": False,"tooltip": "If enabled, forcefully clears the Memory Storage" } ),
			  "AcceptNulls": ("BOOLEAN", { "forceInput": False,"tooltip": "Specifies whether the Memory Storage should ignore Null values" } )
		}, "hidden": { "unique_id": "UNIQUE_ID" }
	  }
	
	#TODO: Add Button that shows the value through RaiseException
	PREV_NAME = ""
	
	RETURN_TYPES = (any_type,)
	RETURN_NAMES = ("Output",)
	OUTPUT_TOOLTIPS = ("Data that will be forwarded to other nodes after caching",)
	FUNCTION = "store"
	CATEGORY = MAIN_CATEGORY
	DESCRIPTION = \
"""This node allows you to set and cache values across multiple executions of your workflow so that you can have persistent data to be manipulated on demand.

To use this node, you must give your variable a UNIQUE and CASE SENSITIVE name by which your data will be referred to elsewhere. This Data may then be accessed in any other nodes from this pack that support the FORMULA output such as the [Data Monitor] and inside Custom Expressions of the [IF Selector] node. Refer to the documentation of those nodes to learn how to access Memory Storages within them.

The Input of this node will set the value of the Memory Storage and additionally forward it as a Passthrough to the node of your choice via its singular Output. If Input is missing, the Node will emit the value associated with the Memory Storage specified by Name.

If Reset is set to true, the Memory Storage associated with this node will be cleared instead. The Output of this node will be NULL regardless of Passthrough. Convert this widget into an input to be able to reset the Memory Storage programatically based on certain conditions.

If AcceptNulls is enabled, you will be able to manually clear the Storage by sending a None type value through Input such as one obtained from the [Null Output] node in this pack. If AcceptNulls is disabled, any None type values will be ignored, allowing you to ensure the memory is set only to valid values. This can be useful, for instance, when connecting a [Memory Storage] node to a [Universal Switch] node as it will ignore any invalid outputs that were not selected and retain its previous value instead. 

HOVER OVER THE INPUTS AND OUTPUTS OF THE NODE FOR MORE INFO.
"""
	
	def store(s, Name, Input=None, Reset=False, AcceptNulls=False,unique_id=0):
   
		global VYKOSX_STORAGE_DATA
		
		if Name == "":
			 raise Exception('ERROR: Name property not set!')
			 return (None,)
			
		if Input is not None:
		
			CurrentValue = None
		
			if Name in VYKOSX_STORAGE_DATA:
				CurrentValue = VYKOSX_STORAGE_DATA[Name]
				s.PREV_NAME = Name
			else:
				if s.PREV_NAME == "":
				 s.PREV_NAME = Name
				elif Name != s.PREV_NAME:
					debug_print(">> MEMORY STORAGE NAME UPDATE FROM '",s.PREV_NAME,"' to '",Name,"'!")
					CurrentValue = VYKOSX_STORAGE_DATA.pop(s.PREV_NAME,Input)
					s.PREV_NAME = Name
					 
			debug_print (">> MEMORY STORAGE [",unique_id,"]: NAME = ",Name," CURRENT = ",CurrentValue,"NEW = ",Input,"RESET = ",Reset) 
		
			VYKOSX_STORAGE_DATA[Name] = Input
			
		else:
		   
			if AcceptNulls:
				Reset = True
	
		if Reset:
			VYKOSX_STORAGE_DATA[Name] = None
			debug_print (">> RESETTING MEMORY STORAGE [",Name,"] TO NONE!")
			
		if Name in VYKOSX_STORAGE_DATA:
		
			display_text = VYKOSX_STORAGE_DATA[Name]
			display_text = repr(display_text).strip("'\"") if type(display_text) is not str else display_text
		
			return {"ui": {"text": display_text}, "result": (VYKOSX_STORAGE_DATA[Name],)}
			#return (VYKOSX_STORAGE_DATA[Name],)
			
		else:
		
			debug_print (">> WARNING: ATTEMPTING TO ACCESS MEMORY STORAGE [",Name,"] BEFORE DEFINITION! RETURNING 'NONE'")
			return {"ui": {"text": ""}, "result": (None,)}
			#return (None,)
	
	@classmethod
	def IS_CHANGED(s, Name, Input=None, Reset=False, AcceptNulls=False,unique_id=0):	
		return float('nan')
		
class InvertCondition:
	
	@classmethod
	def INPUT_TYPES(s):
	  return {
		"required": {			  
			 "input": (any_type,{"tooltip": "Data to forward to other nodes after inverting the condition."}),
			 "mode": ("BOOLEAN", {"default": True, "label_on": "boolean", "label_off": "logical","tooltip": "What kind of NOT will be executed, Boolean or Logical."}), 
		  }
	  }
	  
	RETURN_TYPES = (any_type,)
	RETURN_NAMES = ("output",)
	OUTPUT_TOOLTIPS = ("Data that will be forwarded to other nodes after inversion",)
	FUNCTION = "invert"
	CATEGORY = MAIN_CATEGORY
	DESCRIPTION = \
"""This node is a simple NOT gate that will invert any conditions that go through it (i.e. conditions evaluating to True will become False and vice versa).

If Mode is set to Logical, instead of dooing a Boolean NOT operation a BINARY not will be executed on the value instead. This is meant to be used for numeric values rather than booleans. For more information on how this works, consult the Wikipedia page on 'Two's Complement'.
"""
	
	def invert(self, input, mode):

		if input is None:
			return (True,)
		else:            
			return ( not cbool(Input) , ) if mode else ( ~Input, )
	  

class DelayExecution:
	
	@classmethod
	def INPUT_TYPES(s):
	  return {
		"required": {			  
			  "Delay": ('FLOAT', {"default": 5.0, "forceInput": False,"tooltip": "Length in seconds (or fractions of seconds) to wait for"} ),
		  },
		"optional": {
			   "Input": (any_type,{"tooltip": "Data to forward to other nodes after the waiting period is over"}),
		  },
	  }
	  
	RETURN_TYPES = (any_type,)
	RETURN_NAMES = ("Output",)
	OUTPUT_TOOLTIPS = ("Data that will be forwarded to other nodes after the delay has been processed",)
	FUNCTION = "wait"
	CATEGORY = MAIN_CATEGORY
	DESCRIPTION = \
"""This node allows you to wait for a configurable length of time before resuming execution. This can be useful if your workflow relies on concurrent or time-sensitive operations, or if you simply want some time to grab a cup of coffee in between generations.

You can specify the length of time to wait in seconds by changing the value of Delay. To wait for less than one second, simply specify fractional numbers, such as 0.001 to wait for one millisecond.

This node's implementation of a delay is useful but very naive. It simply instructs the process to be suspended for however long you specify. For a more robust implementation that actually uses a timer and polls it periodically, while still allowing you to cancel out of the waiting period and even has a nifty little screensaver, look no further than the Jovimetrix's [JOV Delay] custom node.
"""
	def wait(self, Delay, Input=[""]):

		debug_print ("Sleeping for ", Delay, " seconds!")
		
		time.sleep(Delay)
		
		debug_print ("Zzzz... Ah there we go, much better!")
		
		return (Input,)
	  
class UnloadModels:
	
	@classmethod
	def INPUT_TYPES(s):
	  return {
		"required": {
			   "Passthrough": (any_type,{"tooltip": "Data to forward to other nodes after cleaning the VRAM"}),
			   "ForceUnload": ("BOOLEAN", { "default": False, "forceInput": False, "label_on": "Unload Models Immediately", "label_off": "Request Model Unloading","tooltip": "Specifies how the models should be unloaded. Instantly or On-Demand"} ),
		  },
		   "hidden": {
			   "node_id": "UNIQUE_ID"
		  }, 
	  }
	 
	RETURN_TYPES = (any_type,)
	RETURN_NAMES = ("Output",)
	OUTPUT_TOOLTIPS = ("Data that will be forwarded to other nodes after cleaning the VRAM",)
	FUNCTION = "unload"
	CATEGORY = MAIN_CATEGORY
	DESCRIPTION = \
"""This node forcefully unloads all models currently loaded by ComfyUI into VRAM. Typically, ComfyUI's memory management does a very good job at managing VRAM automatically to prevent Out of Memory errors. However, on occasion, it may either fail or start paging models into Shared Memory which leads to very slow generation.

If you are having VRAM issues or your workflow utilizes multiple models that do not all need to be loaded to memory simultaneously, it may be very useful to be able to clear them on demand. Simply insert this node in between other operations in your workflow and all the loaded models will be removed from your VRAM.

There are two models of operation depending on the value of ForceUnload. If Enabled, all models will be unloaded immediately, which may cause issues with the workflow if any pending nodes still require access to the model. If Disabled, Model Unloading will be requested instead and ComfyUI will handle unloading it at its earliest convenience. This is analogous to clicking the Unload Model button directly in ComfyUI itself.

HOVER OVER THE INPUTS AND OUTPUTS OF THE NODE FOR MORE INFO.
"""

	def unload(self, Passthrough, ForceUnload, node_id):
			
		if ForceUnload:
		
			debug_print (">> FORCE UNLOADING MODELS...")
				
			mem_manager.unload_all_models()
			mem_manager.soft_empty_cache()
		
		else:
		
			debug_print (">> REQUESTING MODEL UNLOADING...")
				
			PromptServer.instance.send_sync("VykosX.UnloadModels", {"node": node_id})
			
		return (Passthrough,)
		
class GarbageCollector:
	def __init__(self):
		pass
	
	@classmethod
	
	def INPUT_TYPES(s):
	  return {
		"required": {
			  "Input": (any_type,{"tooltip": "Data to forward to other nodes after cleaning the memory"}),
			  "RAM": ("BOOLEAN", { "default": True, "label_on": "Free Unused Memory (Windows only)", "label_off": "Free Unused Memory (Windows only)","tooltip": "Attempt to clear the RAM on Windows systems. Requires WinMemoryCleaner.exe to be placed in the ComfyUI root folder"} ),
			  "Mode": ("BOOLEAN", { "default": False, "label_on": "Run Async. (Requires Admin)", "label_off": "Wait until Complete","tooltip": "Specifies whether to wait for memory cleaning to succeed before continuing"}),
		  }
	  }
	  
	RETURN_TYPES = (any_type,)
	RETURN_NAMES = ("Output",)
	OUTPUT_TOOLTIPS = ("Data that will be forwarded to other nodes after cleaning the memory",)
	FUNCTION = "garbage_collect"
	CATEGORY = MAIN_CATEGORY
	DESCRIPTION = \
"""This node releases any memory currently used by ComfyUI and the underlying framework that is not expressly necessary. It does so by requesting garbage collection from several different sources, including ComfyUI itself, Torch and Python's Garbage Collector.

Use this node to run workflows that are triggering Out of Memory errors due to RAM exhaustion. It may just be enough to let you run a workflow that would otherwise give you errors and not complete. If your issue stems from a lack of VRAM instead, try this node in conjunction with the [Unload Models] node, immediately after it.

The Input and Outputs of this node are a simple passthrough that will forward any data sent through this node, after garbage collection has completed.

IF RAM cleaning is enabled, the node will additionally call WinMemoryCleaner.exe to flush memory from Windows and release unused pages from memory. In order for this functionality to work, WinMemoryCleaner.exe must be downloaded from its respective Github (https://github.com/IgorMundstein/WinMemoryCleaner) and placed within the root ComfyUI folder.

If Mode is set to Run_Async, WinMemoryCleaner.exe will be executed and the workflow execution will continue automatically. This however requires ComfyUI (or rather Python specifically) to be running with Administrative privileges. Otherwise you can use the 'Wait until Completion' mode which does not require administrative privileges and will block execution for a few seconds and resume when the RAM has been thoroughly cleaned and released.

HOVER OVER THE INPUTS AND OUTPUTS OF THE NODE FOR MORE INFORMATION.
"""

	def garbage_collect(self, Input, RAM, Mode):
	
		debug_print(">> TRIGGERING GARBAGE COLLECTION.")
	   
		mem_manager.soft_empty_cache()
		torch.cuda.empty_cache()
		torch.cuda.ipc_collect()
		gc.collect()
		 
		if RAM:
		
			process = "WinMemoryCleaner.exe"
			cmd_line = "/ModifiedPageList /ProcessesWorkingSet /StandbyList /SystemWorkingSet"
		   
			if os.path.isfile(process):
				
				if Mode:
					
					debug_print (">> ATTEMPTING TO CLEAN THE MEMORY WITHOUT INTERRUPTING WORKFLOW EXECUTION...")
				
					try:
						pid = os.spawnl(os.P_NOWAIT , process, cmd_line)
						if pid != 0:
							debug_print (">> SYSTEM MEMORY CLEANING REQUEST SUCCESSFUL!")
						return (Input,)
					except:
						pass
						debug_print (">> UNABLE TO FREE MEMORY ASYNCHRONOUSLY (MAKE SURE TO RUN WITH ADMIN PRIVILEGES)")
					
				debug_print (">> ATTEMPTING TO CLEAN THE MEMORY IN BLOCKING MODE. EXECUTION WILL RESUME ONCE RAM HAS BEEN FREED.")
				
				try:
					os.system(process + " " + cmd_line)
					
					debug_print (">> SYSTEM MEMORY HAS BEEN CLEANED SUCCESSFULLY!")
					
					return (Input,)
				
				except:
					pass
			
			debug_print (">> MEMORY CLEANER PROCESS NOT FOUND OR CANNOT BE EXECUTED. ENSURE 'WinMemoryCleaner.exe' IS PRESENT IN COMFYUI ROOT FOLDER.")
			
		return (Input,)