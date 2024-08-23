"""
@Author: VykosX
@Description: Custom nodes for ComfyUI to enable flow control with advanced loops, conditional branching, logic operations and several other nifty utilities to enhance your ComfyUI workflows
@Title: ControlFlowUtils
@Nickname: ControlFlowUtils
@Version: 0.1.0 ALPHA
@URL: https://github.com/VykosX/ControlFlowUtils
"""
# UNSTABLE ALPHA RELEASE - EXPECT BUGS TO BITE
# PLEASE DO NOT SHARE OUTSIDE OF LINKING TO THE GITHUB

import json
import math
import folder_paths
import os
import torch
import gc
import time
import nodes
import comfy.model_management as mem_manager
from server import PromptServer

from . import Types
any_type = Types.AnyType("*")

MAIN_CATEGORY = "🐺 VykosX-ControlFlowUtils"

DEBUG_MODE = False #Enable this flag to get all sorts of useful debug information in the console from most of the nodes in this pack.

'''
FUNCTION NAME: cbool
PURPOSE: Converts values to Boolean
PARAMETERS:
 - Value (Any): The value to convert
RETURNS: True or False based on whether Value can be interpreted as a Boolean
'''
def cbool(Value):
    if str(Value).lower() in ("yes", "y", "true",  "t", "1"):
        return True
    if str(Value).lower() in ("no",  "n", "false", "f", "0", "0.0", "", "none", "[]", "{}"):
        return False
    raise Exception('Invalid value for boolean conversion:', Value)

'''
FUNCTION NAME: cint
PURPOSE: Converts values to Integer
PARAMETERS:
 - Value (Any): The value to convert
RETURNS: An integer rounded to the nearest even number
'''
def cint(Value):

    d = 0 #How many decimals to round to. For integers this is always 0
    try:
        Value=float(Value)
    except:
        try:
            Value = len(Value)
            if l == 0:
                return 0
        except:
            raise Exception('Invalid value for integer conversion:',x)
    
    p = 10 ** d
    
    if Value > 0:
        z = float(math.floor((Value * p) + 0.5))/p
    else:
        z = float(math.ceil((Value * p) - 0.5))/p        
        
    return int(z)

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
                "start": ("INT", {"default": 0,"forceInput": False}),
                "step": ("INT", {"default": 1,"forceInput": False}),
                "end": ("INT", {"default": 0,"forceInput": False})
            },"optional": {
                "manual_reset": ("BOOLEAN", {"forceInput": False}),
                "auto_reset": ("BOOLEAN", {"forceInput": False, "default": True, "label_on": "Auto Reset on Cycle End", "label_off": "Keep Cycling until Manual Stop" })
            },"hidden": { "node_id": "UNIQUE_ID" },
        }
    
    RETURN_TYPES = ("CYCLE","BOOLEAN")
    RETURN_NAMES = ("CYCLE","RESET?")
    FUNCTION = "run"
    CATEGORY = MAIN_CATEGORY

    def run(self,start,step,end,manual_reset,auto_reset,node_id):
    
        if DEBUG_MODE:
            print (">> CYCLE INIT!")
            
        #PromptServer.instance.send_sync("VykosX.StartCycle", {"node": node_id})
            
        if manual_reset or self.state['finish']:
            if manual_reset or auto_reset:
            
                print (">> CYCLE RESET!")
            
                self.state = {'index': None,'step':step,'end': end, 'start': start, 'finish': False, 'auto_reset': auto_reset}
                
                return (self.state,True)
                
        return (self.state,False)
    
    @classmethod    
    def IS_CHANGED(self, start ,step, end,manual_reset,auto_reset,node_id):
        if reset:
            self.state = {'index': start,'step':step,'end': end, 'start': start, 'finish': False, 'auto_reset': auto_reset}
            return True            
        return False

class CycleStart:
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {"data": any_type, "CYCLE": ("CYCLE",)},
            "optional": {"aux_data": any_type, "index_override": ("INT", {"forceInput": True},) }
        }
      
    RETURN_TYPES = (any_type,any_type,"INT",)
    RETURN_NAMES = ("*","*","index",)
    FUNCTION = "run"
    CATEGORY = MAIN_CATEGORY
    
    def run(self, data, CYCLE, aux_data=None,index_override=None):
    
        if CYCLE['index'] is None:
        
            if DEBUG_MODE:
                print (">> CYCLE START - DRY RUN")
                
            return (None,None,None,)
        
        else:
        
            if index_override is not None:
                CYCLE['index'] = index_override
            
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
            "required": { "data": (any_type,), "CYCLE": ("CYCLE",) },
            "optional": { "aux_data": (any_type,)}            
        }
    
    RETURN_TYPES = ("INT","BOOLEAN",)
    RETURN_NAMES = ("index","finished",)
    FUNCTION = "run"
    CATEGORY = MAIN_CATEGORY
    OUTPUT_NODE = True

    def run(self, data, CYCLE, aux_data=None):
    
        if CYCLE['index'] is None:
            CYCLE['index'] = CYCLE['start']
            if DEBUG_MODE:
                print (">> CYCLE END - DRY RUN")
            return (None,None,None)
        
        if DEBUG_MODE:
            print (">> CYCLE ITERATION '", CYCLE['index'],"'!")
        
        CYCLE['next'] = data
        CYCLE['aux'] = aux_data
        CYCLE['index'] += CYCLE['step']
        
        if CYCLE['step'] >= 0:
            CYCLE['finished'] = ( CYCLE['end']+1 - CYCLE['index'] <= 0 )
        else:
            CYCLE['finished'] = ( CYCLE['end']+1 - CYCLE['index'] >= 0)
            
        if CYCLE['finished'] and CYCLE['auto_reset']:
        
            if DEBUG_MODE:
                print (">> CYCLE AUTO-RESET!")
        
            CYCLE['index'] = CYCLE['start']
        
        return (CYCLE['index'],CYCLE['finished'])
        
    @classmethod
    def IS_CHANGED(s, data, CYCLE, aux_data=None):
        ret = (not CYCLE['finished'])
        if DEBUG_MODE:   
            print ("CYCLE CHANGE:",ret)
        return ret
        

class UniversalSwitch: 

    #TODO: Make input and output amounts dynamic. 
    #      Have a working setting for type validation. 
    
    max_slots = 6
        
    @classmethod
    def INPUT_TYPES(s):
    
        dynamic_inputs = {"input2": (any_type, {"lazy": True}),}
        for x in range(2, s.max_slots+1):
            dynamic_inputs[f"input{x}"] = (any_type, {"lazy": True})
        return {
            "required": { "input1": (any_type, {"lazy": True}),"selection": ("INT", {"default": 1, "min": 0, "max": s.max_slots, "step": 1, "forceInput": False}),"mode": (["SWITCH > ONE","SWITCH > ALL","INV. SWITCH > ONE","INV. SWITCH > ALL","PASSTHROUGH","SORT","REVERSE"],),"validate_typing": ("BOOLEAN", {"forceInput": False}), 
            }, "optional": dynamic_inputs, "hidden": {"prompt": "PROMPT", "unique_id": "UNIQUE_ID","extra_pnginfo": "EXTRA_PNGINFO"},            
        }
        
    def pack_tuple(s,prefix_type,general_type,count):
    
        return tuple([prefix_type] + [general_type for x in range(1,count+1)])
        
    RETURN_TYPES = pack_tuple(None,"INT",any_type,max_slots) #tuple(["INT"] + [any_type for x in range (1,max_slots+1)])
    RETURN_NAMES = tuple([x for x in ["Index"] + list( "*" * max_slots) ]) #tuple('*' * max_slots)      #("Index","*","*","*","*","*",)
    FUNCTION = "switch"
    CATEGORY = MAIN_CATEGORY
    
    def check_lazy_status(s, *args, **kwargs):
    
        selection = int(kwargs['selection'])
        
        if selection == 0:
            inputs = ["input1"]
            for x in range(2,s.max_slots+1):
                inputs.append("input"+str(x))
        else:        
            inputs = [f"input{selection}"]

        if DEBUG_MODE:
            print ("SWITCH [",kwargs['unique_id'],"] LAZY CHECK: ", inputs)
        
        return inputs
    
    def switch(s,input1,mode,selection,validate_typing,**kwargs):
    
        if selection is None:
            return (None*s.max_slots)
    
        def find_output_count(kwargs):
            
            if DEBUG_MODE:
                workflow_info,unique_id,prompt = kwargs.pop('extra_pnginfo'),kwargs.pop('unique_id'),kwargs.pop('prompt')
                #print ("WORKFLOW:",workflow_info,"\n\nUNIQUE_ID:",unique_id,"\n\nPROMPT:",prompt)
                
                print ("\n>> SWITCH [",unique_id,"]")
            
            return 0 #Implement mechanism for returning the index of the first output node that is actually connected to another node
                     #use extra_pinginfo and unique_id
         
        selected_slot = None
        outputs = find_output_count(kwargs)
       
        options = [input1]
        
        for key,value in kwargs.items():
            options.append(value)
        
        if DEBUG_MODE:
            print (">> OPTIONS:",options)
        
        
        if "INV. SWITCH" not in mode:
        
            if selection == 0:
                i=0
                for input in options:
                    i+=1
                    if input is not None:
                        selected_slot = input
                        if DEBUG_MODE:
                            print (">> SELECTED SLOT (FIRST VALID):",i)
                        break
                        
            elif selection > 0:     
                if selection >= len(options):
                    selected_slot = options[len(options)-1]
                else:
                    selected_slot = options[selection-1]
                        
        match mode:
        
            case "SWITCH > ONE":
            
                ret = [selection] + [selected_slot] + [None] * (s.max_slots-1)
        
            case "SWITCH > ALL":
                ret = s.pack_tuple(selection,selected_slot, s.max_slots) 
                
            case "INV. SWITCH > ONE":
            
                ret = [selection] + [None] * (s.max_slots)
                ret[selection] = input1 
            
            case "INV. SWITCH > ALL":
            
                ret = s.pack_tuple(selection,input1, s.max_slots)
            
            #The following operation modes are still untested
            
            case "PASSTHROUGH":
            
                ret = [selection] + options
                
            case "SORT":
            
                ret = [selection] + sorted(options)
                
            case "REVERSE":
            
                ret = [selection] + options[::-1]
                
        print("\n>> RETURN: ", ret)
                
        return ret
 
class IfConditionSelector:

    @classmethod
    def INPUT_TYPES(s):
        return {
              "required": {                             
                    "condition": (["A is TRUE", "B is TRUE", "A is NONE","B is NONE", "A == B", "A != B", "A > B", "A >= B", "A < B", "A <= B","A is B","A is not B","A in B", "B in A", "A & B", "A | B", "A ^ B"],), "comparison_type": (["Values","Length(A)|Value(B)","Length (Both)","Address(A)|Value (B)","Address (Both)","Custom Expression"],),
                    "NOT": ("BOOLEAN",),
                     "A": (any_type, {"forceInput": True, "lazy": True}),
                     "B": (any_type, {"forceInput": True, "lazy": True}),      
            }, "optional": {
                "TRUE_IN": (any_type, {"forceInput": True, "lazy": True}),
                "FALSE_IN": (any_type, {"forceInput": True, "lazy": True}), 
            }, "hidden": { "unique_id": "UNIQUE_ID" }
        
       }
       
    RETURN_TYPES = (any_type,)
    RETURN_NAMES = ("*",)
    FUNCTION = "run_comparison"
    CATEGORY = MAIN_CATEGORY
    
    def compare(self,A,B,condition,comparison_type,NOT):
    
        ret = False
        
        match comparison_type:                    
            
            case "Length(A)|Value(B)":
                A = len(A)
            case "Length (Both)":
                A,B = len(A),len(B)
            case "Address(A)|Value (B)":
                A = id(A)
            case "Address (Both)":
                A,B, = id(A),id(B)
            case "Custom Expression": #UNTESTED! Expected format: (A={Keys:Values}, B=Expression (%Key% to resolve)
                if type(A) is dict:
                    for key, value in my_dict.items():
                        B = B.replace('%'+key+'%',value)
                    return cbool( eval(B) )
                    
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
    
        if NOT: 
            ret = ~ret
        
        return ret
            
    def run_comparison(s,condition,comparison_type,NOT,A,B,TRUE_IN=None,FALSE_IN=None,unique_id=0):
    
        print ("\n>> IF CONDITION [",unique_id,"]")
        
        print (">> COMPARE! A:",A,"B:",B,"cond:",condition,"comp:",comparison_type,"NOT:",NOT,"TRUE:",TRUE_IN,"FALSE:",FALSE_IN)
    
        ret = s.compare(A,B,condition,comparison_type,NOT)
        
        print (">> COMPARE RESULT:",ret)
    
        return (TRUE_IN,) if ret else (FALSE_IN,)
    
    def check_lazy_status(s,condition,comparison_type,NOT,A,B,TRUE_IN=None,FALSE_IN=None,unique_id=0):
    
        print (">> IF LAZY CHECK! A:",A,"B:",B,"cond:",condition,"comp:",comparison_type,"NOT:",NOT,"TRUE:",TRUE_IN,"FALSE:",FALSE_IN)
    
        ret = s.compare(A,B,condition,comparison_type,NOT)

        lazy = ["A","B"] #Decided to make both A and B required. Pass NULL Output to whichever one is not in use if needed.
        lazy += ["TRUE_IN"] if ret else ["FALSE_IN"]
    
        print (">> LAZY RESULT:",lazy)
        return lazy

class HaltExecution:

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "disable": ("BOOLEAN", {"default": False, "forceInput": False}),
                "clear_queue": ("BOOLEAN", {"default": False, "forceInput": False}),
                "input": (any_type,),
            }, "optional": { "aux": (any_type,), }
        }

    RETURN_TYPES = (any_type,)
    RETURN_NAMES = ("*",)
    CATEGORY = MAIN_CATEGORY
    FUNCTION = "halt"

    def halt(s,disable,clear_queue,input, aux=None):
    
        print (" >> ATTEMPTING HALT!",disable,input, )
    
        if not disable and input is not None:
        
            if DEBUG_MODE:
                print ("\n"+"-"*36+"\n      # HALTING EXECUTION #"+"\n"+"-"*36)           
        
            if clear_queue:        
                PromptServer.instance.send_sync("VykosX.ClearQueue", {}) #Not working currently
            
            nodes.interrupt_processing(True)
            
            return (None,)
            
        return (input,)
      
class DataMonitor:
    
    def __init__(self):
        pass
        
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
               "text":("STRING", {"default": '',"multiline": True,"forceInput": False,"print_to_screen": True}),
               "output_type": (["ANY","STRING","INT","FLOAT","BOOLEAN","LIST","TUPLE","JSON","FORMULA"],),
            },
               "optional": {
                   "passthrough":(any_type, {"default": "","multiline": True,"forceInput": True}),
                   "aux":(any_type, {"default": "","forceInput": True}),                   
               }, "hidden": { "unique_id": "UNIQUE_ID" }
        }
    
    RETURN_TYPES = (any_type,)
    RETURN_NAMES = ("output",)
    FUNCTION = "data_monitor"
    OUTPUT_NODE = True
    CATEGORY = MAIN_CATEGORY

    def data_monitor(self,text="",output_type="ANY",passthrough=None,aux=None,unique_id=0):
    
        #TODO:
        #Add %prev% for the previous value set, %clear% to empty the text via aux, $mem$ to resolve to the value of memory storage nodes and and %var% to resolve to the value of mape variables/KJNodes get/set/ and anything everywhere nodes
        
        def replace_aux(text_value,aux_value):
            
            print ("text:", text_value,"aux:",aux_value)
              
            if text_value is not None:
              
                if aux_value is None:
                    aux_value = ""
                    print ("text:", text_value,"aux:",aux_value)
                
                try:
                    s = str(text_value)
                    try:
                        x = str(aux_value)
                        
                        print ("str_text:", s,"str_aux",x)
                        
                        if s!="" and "%aux%" in s:      
                            if DEBUG_MODE:
                                print ('REPLACING %AUX% in "'+s+'" with "'+x+'"!')
                            
                            return s.replace("%aux%",x)
                    except:
                        pass
                except:
                    pass
                                  
            return text_value
    
        #CHECK HOW DISPLAY ANY RENDERS LATENT IMAGE (if type=dict). Currently crashes.
        
        if DEBUG_MODE:
        
            print ("\n>> DATA MONITOR [",unique_id,"]")         
            print( "PASSTHROUGH: ", type(passthrough), repr(passthrough) )
            print( "AUX: ", type(aux), repr(aux), "[",aux,"]" )
            print( "OUTPUT TYPE: ", output_type)
                
        if (passthrough is not None):                

            encapsulate = False
            
            try:
                iterator = iter(passthrough)
            except TypeError:    
                encapsulate = True
                if DEBUG_MODE:
                    print ("[!] PASSTHROUGH NOT ITERABLE!")                                
            else:            
                if DEBUG_MODE:
                    print ("[!] PASSTHROUGH ITERABLE!")
                try:
                    float(passthrough)                    
                except:
                    if DEBUG_MODE:
                        print ("[!] PASSTHROUGH NOT NUMERIC!")                    
                else:
                    if DEBUG_MODE:
                        print ("[!] PASSTHROUGH NUMERIC!")
                    encapsulate = True
                    
            if DEBUG_MODE:
                print("OUTPUT TYPE: ", output_type)

            ret = replace_aux(passthrough,aux)

            if ret == "":
                return text,
            else:
                text = ret
            
            if DEBUG_MODE:
                print ( "TEXT:", text )    
            
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
                case "JSON":                         
                    text = json.loads(text),                    
                case "FORMULA":
                    if text != "":
                        text = eval(str(text))
                    try:
                        float(text)                    
                    except ValueError:
                        if DEBUG_MODE:
                            print ("PASSTHROUGH FORMULA NOT NUMERIC!")                    
                    else:
                        if DEBUG_MODE:
                            print ("PASSTHROUGH FORMULA NUMERIC!")
                        encapsulate = True
                case _:
                    text = passthrough
            
            if DEBUG_MODE:
                print ("RETURN [PASSTHROUGH]:",type(text), repr(text))
            
            if encapsulate:
                return {"ui": {"text": tuple([text]) },"result": tuple([text]) }
            else:
                return {"ui": {"text": text},"result": (text,)}
        else:

            if DEBUG_MODE:
                print("TEXT: ", type(text), repr(text))

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
                        text = eval(str(text))
            
            if DEBUG_MODE:
                print ("RETURN [TEXT]:",text)

            return text,

class CheckpointSelector:
    
    @classmethod
    def INPUT_TYPES(s):
        CHECKPOINT_LIST = sorted(folder_paths.get_filename_list("checkpoints"), key=str.lower)
        return {
            "required": { 
                "checkpoints": (CHECKPOINT_LIST, ),
                }, "optional": {
                "aux":(any_type, {"default": "","forceInput": True})
                }
            }
            
    RETURN_TYPES = (any_type,)
    RETURN_NAMES = ("Checkpoint",)    
    FUNCTION = "load_checkpoints"
    CATEGORY = MAIN_CATEGORY
    
    def load_checkpoints(self, checkpoints,aux=None) -> any_type:            
        return (checkpoints,)
        
class LoraSelector:
    
    @classmethod
    def INPUT_TYPES(s):
        LORA_LIST = sorted(folder_paths.get_filename_list("loras"), key=str.lower)
        return {
            "required": { 
                "lora_name": (LORA_LIST, ),
                }, "optional": {
                "aux":(any_type, {"default": "","forceInput": True})
                }
            }
            
    RETURN_TYPES = (any_type,)
    RETURN_NAMES = ("LoRA",)    
    FUNCTION = "load_lora"
    CATEGORY = MAIN_CATEGORY
    
    def load_lora(self, lora_name,aux=None) -> any_type:            
        return (lora_name,)
        
class VAESelector:
    
    @classmethod
    def INPUT_TYPES(s):
        VAE_LIST = sorted(folder_paths.get_filename_list("vae"), key=str.lower) + ["taesd","taesdxl"]
        return {
            "required": { 
                "vae": (VAE_LIST, ),
             }, "optional": {
                "aux":(any_type, {"default": "","forceInput": True})
             }
        }
    RETURN_TYPES = (any_type,)
    RETURN_NAMES = ("VAE Name",)    
    FUNCTION = "load_vaes"
    CATEGORY = MAIN_CATEGORY
    
    def load_vaes(self, vae, aux=None) -> any_type:            
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
    
    def return_null(self,NULL):
        return (None,)

class NullOutput:

    @classmethod
    def INPUT_TYPES(cls):
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
    
    def return_null(self):
        return (None,)
        
class ImageResolutionAdjust:
    
    @classmethod
    def INPUT_TYPES(s):
    
        MAX_RESOLUTION = 8192
        
        return {"required": { "source_width": ("INT", {"default": 512, "min": 16, "max": MAX_RESOLUTION, "step": 8}),
                              "source_height": ("INT", {"default": 512, "min": 16, "max": MAX_RESOLUTION, "step": 8}),
                              "scaling_factor": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 10, "step": 0.1}),
                              "target_width": ("INT", {"default": 512, "min": 16, "max": MAX_RESOLUTION, "step": 8}),
                              "target_height": ("INT", {"default": 512, "min": 16, "max": MAX_RESOLUTION, "step": 8}),
                              "tolerance": ("INT", {"default": 32, "min": 16, "max": 1024})
                              }
               }
    RETURN_TYPES = ("INT","INT","STRING")
    RETURN_NAMES = ("Adj. Width","Adj. Height","Result")    
    FUNCTION = "adjust_res"
    CATEGORY = MAIN_CATEGORY
    
    def adjust_res (self, source_width: int, source_height: int,scaling_factor: float, target_width: int, target_height: int,tolerance:int):
    
        if DEBUG_MODE:
            print("W: ",source_width,"H: ",source_height,"DW: ",target_width,"DH: ",target_height,"T: ",tolerance)
    
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
                if DEBUG_MODE:
                    print ("Maintaining Target Resolution")
                return (target_width,target_height,0)
            else:
                if DEBUG_MODE:
                    print("Resolution Override - Using Scaling Factor")

        w_diff,h_diff = 1,1

        if DEBUG_MODE:
            print("Src W: ", width,"Src H:",height,"Target W:",target_width,"Target H:",target_height)
            print("Src S: ", width*height,"Target S:",target_width*target_height)
            print("W diff: ", w_diff,"H diff: ",h_diff)
            
        if scaling_factor == 1:
            w_diff = width / target_width
            h_diff = target_height / height            
        else:        
            w_diff,h_diff = 1/scaling_factor,1/scaling_factor

        if DEBUG_MODE:
            print("W diff: ", w_diff,"H diff: ",h_diff)
        
        if h_diff != 1:
            if DEBUG_MODE:
                print(">> Adjusted Width")
            target_width = self.round_to_multiple (target_width/h_diff,tolerance)
          
        if w_diff != 1:
            if DEBUG_MODE:
                print(">> Adjusted Height")
            target_height = self.round_to_multiple (target_height*w_diff,tolerance)

        if DEBUG_MODE:
            print("New W:",target_width,"New H:",target_height,"New S:",target_width*target_height)
        
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

    @classmethod
    def IS_CHANGED(self, **kwargs):
        return os.path.getmtime(kwargs['file'])
        
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "file": ("STRING", {"default": "file.txt"}) 
            }
        }

    FUNCTION = "load_text"
    RETURN_TYPES = ("STRING",)
    CATEGORY = MAIN_CATEGORY
    
    def load_text(self, file):
    
        if file is not None:
            if os.path.isfile(file):
                with open(file, "r") as f:
                    return (f.read(), )
                    
        return ("",)

class SaveTextFile():
    
    @classmethod
    def IS_CHANGED(self, **kwargs):
        return float("nan")
        
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {                
                "file": ("STRING", {"default": "file.txt"}),
                "append": (["append", "overwrite", "new only"], {}),
                "insert": ("BOOLEAN", {
                    "default": True, "label_on": "new line", "label_off": "none",
                    "vykosx.binding": [{
                        "source": "append",
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
                "text": ("STRING", {"multiline": True})
            },
        }
    
    RETURN_TYPES = ()
    CATEGORY = MAIN_CATEGORY
    OUTPUT_NODE = True
    FUNCTION = "write_text"

    def write_text(self, file, append, insert, text):
    
        if append == "new only" and os.path.exists(file):
            raise Exception("File already exists and 'new only' is selected.")
            Return (False,)
            
        with open(file, "a+" if append == "append" else "w") as f:
        
            is_append = f.tell() != 0
            
            if is_append and insert:
                f.write("\n")
                
            f.write(text)
            
            return (True,)

        return (False,)
 

class MemoryStorage:
    
    @classmethod
    def INPUT_TYPES(s):
      return {
        "required": {			  
              "Input": (any_type,),
              "Name": ("STRING", { "forceInput": False } ),
        }, "optional": {
              "Reset": ("BOOLEAN", { "forceInput": False } ),
              
        }
	  }
      
    RETURN_TYPES = (any_type,)
    RETURN_NAMES = ("Output",)    
    FUNCTION = "store"
    CATEGORY = MAIN_CATEGORY
    
    Data = None
    
    def store(s, Input, Name, Reset):
    
        if DEBUG_MODE:
            print (">> MEMORY STORAGE [",Name,"]: CURRENT = ",s.Data,"NEW = ",Input,"RESET = ",Reset) 
    
        if Reset:
            s.Data = None
    
        elif Input is not None:
            s.Data = Input
            
        return (s.Data,) 
    
class DelayExecution:
    
    @classmethod
    def INPUT_TYPES(s):
      return {
        "required": {			  
              "Delay": ('FLOAT', {"default": 5.0, "forceInput": False } ),
		  },
        "optional": {
               "Input": (any_type,),
          },
	  }
      
    RETURN_TYPES = (any_type,)
    RETURN_NAMES = ("Output",)    
    FUNCTION = "wait"
    CATEGORY = MAIN_CATEGORY
    
    def wait(self, Delay, Input=[""]):

        if DEBUG_MODE:
            print ("Sleeping for ", Delay, " seconds!")
        time.sleep(Delay)
        
        if DEBUG_MODE:
            print ("Zzzz... Ah there we go, much better!")
        
        return (Input,)
      
class UnloadModels:
    
    @classmethod
    def INPUT_TYPES(s):
      return {
        "required": {
               "Passthrough": (any_type,),
               "ForceUnload": ("BOOLEAN", { "default": False, "forceInput": False, "label_on": "Unload Models Immediately", "label_off": "Request Model Unloading" } ),
               "PurgeTensors": ("BOOLEAN", { "default": False, "forceInput": False, "label_on": "Force Purging Tensors (May Cause Issues)", "label_off": "Disabled"} )
          },
           "hidden": {
               "node_id": "UNIQUE_ID"
          }, 
	  }
     
    RETURN_TYPES = (any_type,)
    RETURN_NAMES = ("Output",)    
    FUNCTION = "unload"
    CATEGORY = MAIN_CATEGORY
    
    def unload(self, Passthrough, ForceUnload, PurgeTensors, node_id):
            
        if ForceUnload:
        
            if DEBUG_MODE:     
                print (">> FORCE UNLOADING MODELS...")
                
            mem_manager.unload_all_models()
            mem_manager.soft_empty_cache()
        
        else:
        
            if DEBUG_MODE:  
                print (">> REQUESTING MODEL UNLOADING...")
                
            PromptServer.instance.send_sync("VykosX.UnloadModels", {"node": node_id})
        
        if PurgeTensors:

            if DEBUG_MODE:
                print (">> ATTEMPTING TO PURGE ALL TENSOR OBJECTS FROM VRAM. BRACE YOURSELF AND HOPE FOR THE BEST.")
                
            self.clear_tensors()
            clear = torch.empty((0,1))
            torch.Tensor.set_(clear)
            
        return (Passthrough,)
        
    #This attempts to find all tensor objects in memory and clear them. Very unsafe, mostly here for testing reasons.
    def clear_tensors(self, only_cuda=False, omit_objs=[]):

        add_all_tensors = False if only_cuda is True else True
        # To avoid counting the same tensor twice, create a dictionary of tensors,
        # each one identified by its id (the in memory address).
        tensors = {}
        i = 0
        
        # omit_obj_ids = [id(obj) for obj in omit_objs]

        def add_tensor(obj):
            if torch.is_tensor(obj):
                tensor = obj
            elif hasattr(obj, 'data') and torch.is_tensor(obj.data):
                tensor = obj.data
            else:
                return

            if (only_cuda and tensor.is_cuda) or add_all_tensors:
                tensors[id(tensor)] = tensor
        
        for obj in gc.get_objects():
            try:
                # Add the obj if it is a tensor.
                add_tensor(obj)
                # Some tensors are "saved & hidden" for the backward pass.
                if hasattr(obj, 'saved_tensors') and (id(obj) not in omit_objs):
                    for tensor_obj in obj.saved_tensors:
                        add_tensor(tensor_obj)
                        i+=1
                        if DEBUG_MODE:
                            print (">> TENSORS FOUND: ",i)
                        
            except Exception as ex:
                pass
                #print(">> EXCEPTION: ", ex)
                # logger.debug(f"Exception: {str(ex)}")
        
        if DEBUG_MODE:
            print (">> [" , i , "] TENSOR OBJECTS FOUND.")
            
        i = 0
        
        for x in tensors.values():
        
            i+=1
            
            if DEBUG_MODE:            
                print (">> Tensor '", i, "': ", type(x))
                try:
                    print (x.type(), x.nbytes,x.itemsize)
                except:
                    print (x.nbytes,x.itemsize)
                    pass
                
            if x.is_cuda:
            
                if DEBUG_MODE:
                    print (">> Dettaching Tensor '",i, "'.")
            
                x.detach()
                x.grad = None
                x.resize_(0)
                
        return #tensors.values()  # return a list of detected tensor
        
class GarbageCollector:
    def __init__(self):
        pass
    
    @classmethod
    
    def INPUT_TYPES(s):
      return {
        "required": {
			  "Input": (any_type,),
              "RAM": ("BOOLEAN", { "default": True, "label_on": "Free Unused Memory (Windows only)", "label_off": "Free Unused Memory (Windows only)"} ),
              "Mode": ("BOOLEAN", { "default": False, "label_on": "Run Async. (Requires Admin)", "label_off": "Wait until Complete"}),
		  }
	  }
      
    RETURN_TYPES = (any_type,)
    RETURN_NAMES = ("Output",)    
    FUNCTION = "garbage_collect"
    CATEGORY = MAIN_CATEGORY

    def garbage_collect(self, Input, RAM, Mode):
    
        if DEBUG_MODE:
            print(">> TRIGGERING GARBAGE COLLECTION.")
       
        gc.collect()
        #mem_manager.soft_empty_cache()
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()
         
        if RAM:
        
            process = "WinMemoryCleaner.exe"
            cmd_line = "/ModifiedPageList /ProcessesWorkingSet /StandbyList /SystemWorkingSet"
           
            if os.path.isfile(process):
                
                if Mode:
                    
                    print (">> ATTEMPTING TO CLEAN THE MEMORY WITHOUT INTERRUPTING WORKFLOW EXECUTION...")
                
                    try:
                        pid = os.spawnl(os.P_NOWAIT , process, cmd_line)
                        if pid != 0:
                            print (">> SYSTEM MEMORY CLEANING REQUEST SUCCESSFUL!")
                        return (Input,)
                    except:
                        pass
                        print (">> UNABLE TO FREE MEMORY ASYNCHRONOUSLY (MAKE SURE TO RUN WITH ADMIN PRIVILEGES)")
                    
                print (">> ATTEMPTING TO CLEAN THE MEMORY IN BLOCKING MODE. EXECUTION WILL RESUME ONCE RAM HAS BEEN FREED.")
                
                try:
                    os.system(process + " " + cmd_line)
                    print (">> SYSTEM MEMORY HAS BEEN CLEANED SUCCESSFULLY!")
                    return (Input,)
                except:
                    pass
            
            print (">> MEMORY CLEANER PROCESS NOT FOUND OR CANNOT BE EXECUTED. ENSURE 'WinMemoryCleaner.exe' IS PRESENT IN COMFYUI ROOT FOLDER.")
            
        return (Input,)