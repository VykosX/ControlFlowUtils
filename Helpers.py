import ast
import operator
import math
import random
import fnmatch
import os

DEBUG_MODE = True #Enable this flag to get all sorts of useful debug information in the console from most of the nodes in this pack.

# HELPER FUNCTIONS
#******************
'''
FUNCTION NAME: cbool
PURPOSE: Converts values to Boolean
PARAMETERS:
 - value (Any): The value to convert
RETURNS: True or False based on whether value can be interpreted as a Boolean
'''

def debug_print(*args,end=" "):
	if DEBUG_MODE:
		print(end.join(map(str, args)),sep="")

	
def cbool(value):
	if str(value).lower() in ("yes", "y", "true",  "t", "1"):
		return True
	if str(value).lower() in ("no",	 "n", "false", "f", "0", "0.0", "", "none", "[]", "{}"):
		return False
	raise Exception('Invalid value for boolean conversion:', value)

'''
FUNCTION NAME: cint
PURPOSE: Converts values to Integer
PARAMETERS:
 - value (Any): The value to convert
RETURNS: An integer rounded to the nearest even number
'''
def cint(value):

	if value == "":
		return 0

	d = 0 #How many decimals to round to. For integers this is always 0
	try:
		value=float(value)
	except:
		try:
			value = len(value)
			if l == 0:
				return 0
		except:
			raise Exception('Invalid value for integer conversion:',value)
	
	p = 10 ** d
	
	if value > 0:
		z = float(math.floor((value * p) + 0.5))/p
	else:
		z = float(math.ceil((value * p) - 0.5))/p		 
		
	return int(z)

def is_list(x):
	
	if type(x) is str:
		return False
	
	try:
		iter(x)
		return True
	
	except TypeError:
		return False
		
def search_folder(folder_path, pattern, recursive, full_path, include_directories,relative_filenames):
	
	if relative_filenames == True:
		relative_filenames = folder_path
	elif relative_filenames == False:
		relative_filenames = ""
		
	entries = os.scandir(folder_path)
	
	try:
		for entry in entries:
			if fnmatch.fnmatch(entry.name, pattern):
				if entry.is_file() or (include_directories and entry.is_dir()):
					if not full_path:
						if relative_filenames!="":
							yield os.path.relpath(entry.path,relative_filenames)
						else:
							yield entry.name
					else:
						yield entry.path
			if entry.is_dir() and recursive:
				yield from search_folder(entry.path, pattern, recursive, full_path, include_directories,relative_filenames)
	finally:
		entries.close()
		
"""		
def search_folder(folder_path, pattern, recursive,full_path,include_directories):
	with os.scandir(folder_path) as files:
		for f in files:
			if fnmatch.fnmatch(f.name, pattern):
				if f.is_file() or (include_directories and f.is_dir()): 
					if not full_path:
						yield os.path.relpath(f.path,folder_path)
					else:
						yield f.path
				if f.is_dir() and recursive: yield from search_folder(f.path, pattern, recursive, full_path,include_directories)
"""

"""
def search_folder(folder_path, pattern, recursive,full_path,include_directories):
	with os.scandir(folder_path) as files:
		for f in files:
			if f.is_file() and fnmatch.fnmatch(f.name, pattern):
				if not full_path:
					print ("RET =", os.path.relpath(f.path,folder_path), " FROM ",f.path)
					yield os.path.relpath(f.path,folder_path)
				else:
					yield f.path
			elif f.is_dir():
				if not full_path:
					yield os.path.relpath(f.path,folder_path)
				else:
					yield f.path
				if recursive: yield from search_folder(f.path, pattern, recursive, full_path,include_directories)
"""
def word_test(op,expr):

	if op is None or op == "":
		return False
	
	result = False
	
	try:
		
		if len(expr) != 0: 
					
			if not is_list(expr):
				expr = [expr]
			
			for x in expr:

				for y in  " ".join(str(x).splitlines()).split(" "):
					
					match op.casefold():
						case "alpha":
							result = ( y.isalpha() ) if y!="" else True
						case "numeric":
							print ("Y=",y)
							if y!= "":
								try:
									float(y)
									result = True
								except ValueError:
									pass
									return False
							else:
								result = True
							#if y!= "": y = y.replace('.','').replace('+','').replace('-','')
							#result = (y.isdigit() ) if y!="" else True
						case _:
							return False
							
					if not result:
						return False
	except:
		pass
	
	return result
		
def extract_between(expr,token1,token2=None):
	
	ret = []
		
	if token2 is None:
		token2 = token1
	
	if token1 == token2:
	
		tmp=expr.split(token1)

		try:
			for x in range(1,len(tmp)-1,2):
				ret.append (tmp[x])
		except:
			pass
			
	else:
	
		i = len(expr)
		
		while (i != 0):
		
			L = expr.partition(token1)[2]
			R = L.partition(token2)[0]
			expr = L[ len(R)+len(token2):]
			i = len(expr)
			if (R!="" and L!=R): ret.append (R)
			
	return ret
	
def replace_caseless(text="", old="",new="",max=0):

	idx,c = 0,0
	
	if old is None: old = ""
	if new is None: new = ""
	
	while idx < len(text):
		
		index_l = text.casefold().find(old.casefold(), idx)
		
		if index_l == -1:
			return text
		
		text = text[:index_l] + new + text[index_l + len(old):]
		idx = index_l + len(new)
		
		c+=1
		if c == max:
			break
			
	return text

import ast
import operator
import math
import random

# Define supported operators
operators = {
	ast.Add: operator.add,
	ast.Sub: operator.sub,
	ast.Mult: operator.mul,
	ast.Div: operator.truediv,
	ast.FloorDiv: operator.floordiv,
	ast.Mod: operator.mod,
	ast.Pow: operator.pow,
	ast.BitXor: operator.xor,
	ast.USub: operator.neg,
	ast.UAdd: operator.pos,	 # Unary addition
	ast.Invert: operator.inv,  # Bitwise inversion
	ast.Eq: operator.eq,
	ast.NotEq: operator.ne,
	ast.Lt: operator.lt,
	ast.LtE: operator.le,
	ast.Gt: operator.gt,
	ast.GtE: operator.ge,
	ast.And: operator.and_,
	ast.Or: operator.or_,
	ast.Not: operator.not_,
	ast.Is: operator.is_,
	ast.IsNot: operator.is_not,
	ast.In: lambda x, y: operator.contains(y, x),
	ast.NotIn: lambda x, y: not operator.contains(y, x),
	ast.BitAnd: operator.and_,
	ast.BitOr: operator.or_,
	ast.LShift: operator.lshift,
	ast.RShift: operator.rshift,
	ast.MatMult: operator.matmul,  # Matrix multiplication
}

# Define supported functions
default_functions = {
	'abs': abs,
	'all': all,
	'any': any,
	'ascii': ascii,
	'bin': bin,
	'bool': bool,
	'chr': chr,
	'dict': dict,
	'divmod': divmod,
	'enumerate': enumerate,
	'filter': filter,
	'float': float,
	'format': format,
	'hex': hex,
	'id': id,
	'int': int,
	'len': len,
	'list': list,
	'map': map,
	'max': max,
	'min': min,
	'oct': oct,
	'ord': ord,
	'pow': pow,
	'print': print,
	'range': range,
	'repr': repr,
	'reversed': reversed,
	'round': round,
	'set': set,
	'sorted': sorted,
	'str': str,
	'sum': sum,
	'tuple': tuple,
	'type': type,
	'zip': zip,
	'math': math,
	'random': random,
	'randrange': random.randrange,
	'randint': random.randint,
	'choice': random.choice,
	'shuffle': random.shuffle,
	'sample': random.sample,
	'uniform': random.uniform,
	'rnd': random.random,
	'seed': random.seed,
}

def safe_eval(expr, variables=None, additional_functions=None):
	"""
	Safely evaluate a mathematical expression with named variables, including list and dictionary indexing,
	logical operators, predefined function calls, list comprehensions, and conditionals.
	
	:param expr: The expression to evaluate as a string.
	:param variables: A dictionary of variable names and their values.
	:param additional_functions: A dictionary of additional functions to support.
	:return: The result of the evaluated expression.
	"""
	if variables is None:
		variables = {}

	if additional_functions is None:
		additional_functions = {}

	# Merge default functions with additional functions
	functions = {**default_functions, **additional_functions}

	# Parse expression into AST
	node = ast.parse(expr, mode='exec')

	def _eval(node, local_vars=None):
		if local_vars is None:
			local_vars = {}

		if isinstance(node, ast.Expression):
			return _eval(node.body, local_vars)
		elif isinstance(node, ast.Assign):
			targets = node.targets
			if len(targets) != 1:
				raise ValueError("Only single target assignments are supported")
			target = targets[0]
			value = _eval(node.value, local_vars)
			if isinstance(target, ast.Tuple):
				if not isinstance(value, (tuple, list)) or len(target.elts) != len(value):
					raise ValueError("Mismatch between tuple assignment and values")
				for elt, val in zip(target.elts, value):
					if not isinstance(elt, ast.Name):
						raise ValueError("Only simple variable assignments are supported")
					local_vars[elt.id] = val
			else:
				if not isinstance(target, ast.Name):
					raise ValueError("Only simple variable assignments are supported")
				local_vars[target.id] = value
			return value
		elif isinstance(node, ast.NamedExpr):  # Handling the walrus operator :=
			target = node.target
			value = _eval(node.value, local_vars)
			if isinstance(target, ast.Tuple):
				if not isinstance(value, (tuple, list)) or len(target.elts) != len(value):
					raise ValueError("Mismatch between tuple assignment and values")
				for elt, val in zip(target.elts, value):
					if not isinstance(elt, ast.Name):
						raise ValueError("Only simple variable assignments are supported")
					local_vars[elt.id] = val
			else:
				if not isinstance(target, ast.Name):
					raise ValueError("Only simple variable assignments are supported")
				local_vars[target.id] = value
			return value
		elif isinstance(node, ast.BinOp):
			left = _eval(node.left, local_vars)
			right = _eval(node.right, local_vars)
			return operators[type(node.op)](left, right)
		elif isinstance(node, ast.UnaryOp):
			operand = _eval(node.operand, local_vars)
			return operators[type(node.op)](operand)
		elif isinstance(node, ast.BoolOp):
			if isinstance(node.op, ast.And):
				for value in node.values:
					result = _eval(value, local_vars)
					if not result:
						return result
				return result
			elif isinstance(node.op, ast.Or):
				for value in node.values:
					result = _eval(value, local_vars)
					if result:
						return result
				return result
		elif isinstance(node, ast.Compare):
			left = _eval(node.left, local_vars)
			for operation, comparator in zip(node.ops, node.comparators):
				right = _eval(comparator, local_vars)
				if not operators[type(operation)](left, right):
					return False
				left = right
			return True
		elif isinstance(node, ast.Num):	 # For Python 3.8 and earlier
			return node.n
		elif isinstance(node, ast.Constant):  # For Python 3.8 and later
			return node.value
		elif isinstance(node, ast.Name):
			if node.id in local_vars:
				return local_vars[node.id]
			elif node.id in variables:
				return variables[node.id]
			elif node.id in functions:
				return functions[node.id]
			elif node.id in {'True', 'False', 'None'}:
				return {'True': True, 'False': False, 'None': None}[node.id]
			else:
				raise NameError(f"Variable '{node.id}' is not defined")
		elif isinstance(node, ast.Subscript):
			value = _eval(node.value, local_vars)
			index = _eval(node.slice, local_vars)
			return value[index]
		elif isinstance(node, ast.Index):  # For Python 3.8 and earlier
			return _eval(node.value, local_vars)
		elif isinstance(node, ast.Slice):
			lower = _eval(node.lower, local_vars) if node.lower else None
			upper = _eval(node.upper, local_vars) if node.upper else None
			step = _eval(node.step, local_vars) if node.step else None
			return slice(lower, upper, step)
		elif isinstance(node, ast.Tuple):
			return tuple(_eval(elt, local_vars) for elt in node.elts)
		elif isinstance(node, ast.List):
			return [_eval(elt, local_vars) for elt in node.elts]
		elif isinstance(node, ast.Dict):
			return {_eval(key, local_vars): _eval(value, local_vars) for key, value in zip(node.keys, node.values)}
		elif isinstance(node, ast.Call):
			func = _eval(node.func, local_vars)
			args = [_eval(arg, local_vars) for arg in node.args]
			if callable(func):
				return func(*args)
			else:
				raise TypeError(f"Unsupported function: {func}")
		elif isinstance(node, ast.Attribute):
			value = _eval(node.value, local_vars)
			if hasattr(value, node.attr):
				return getattr(value, node.attr)
			else:
				raise AttributeError(f"Attribute '{node.attr}' not found in {value}")
		elif isinstance(node, ast.IfExp):
			test = _eval(node.test, local_vars)
			if test:
				return _eval(node.body, local_vars)
			else:
				return _eval(node.orelse, local_vars)
		elif isinstance(node, ast.ListComp):
			elt = node.elt
			generators = node.generators
			return _eval_listcomp(elt, generators, local_vars)
		elif isinstance(node, ast.Lambda):
			return _eval_lambda(node, local_vars)
		elif isinstance(node, ast.Expr):
			return _eval(node.value, local_vars)
		elif isinstance(node, ast.Module):
			for stmt in node.body:
				result = _eval(stmt, local_vars)
			return result
		else:
			raise TypeError(f"Unsupported type: {type(node)}")

	def _eval_listcomp(elt, generators, local_vars):
		"""
		Evaluate a list comprehension.
		
		:param elt: The element expression of the list comprehension.
		:param generators: The generators of the list comprehension.
		:param local_vars: The local variables for the list comprehension.
		:return: The evaluated list comprehension.
		"""
		if not generators:
			return [_eval(elt, local_vars)]

		gen = generators[0]
		iter_ = _eval(gen.iter, local_vars)
		result = []

		for item in iter_:
			new_local_vars = local_vars.copy()
			if isinstance(gen.target, ast.Name):
				new_local_vars[gen.target.id] = item
			elif isinstance(gen.target, ast.Tuple):
				if isinstance(item, tuple) and len(gen.target.elts) == len(item):
					for elt, value in zip(gen.target.elts, item):
						new_local_vars[elt.id] = value
				else:
					raise ValueError("Invalid tuple unpacking in list comprehension")
			if all(_eval(cond, new_local_vars) for cond in gen.ifs):
				result.extend(_eval_listcomp(elt, generators[1:], new_local_vars))

		return result

	def _eval_lambda(node, local_vars):
		"""
		Evaluate a lambda function.
		
		:param node: The lambda node.
		:param local_vars: The local variables for the lambda function.
		:return: The evaluated lambda function.
		"""
		if not isinstance(node, ast.Lambda):
			raise TypeError(f"Expected ast.Lambda, got {type(node)}")

		arg_names = [arg.arg for arg in node.args.args]

		def lambda_func(*args):
			if len(args) != len(arg_names):
				raise TypeError(f"Expected {len(arg_names)} arguments, got {len(args)}")
			lambda_local_vars = local_vars.copy()
			lambda_local_vars.update(zip(arg_names, args))
			return _eval(node.body, lambda_local_vars)

		return lambda_func

	return _eval(node, variables)

"""
# Example usage:
variables = {
	'x': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
	'y': 5,
	'z': {'a': 1, 'b': 2},
	'a': 3,
	'b': 4
}
expression1 = "x[y] + 2 ** 3"
result1 = safe_eval(expression1, variables)
print(result1)	# Output: 13

expression2 = "z['a'] + z['b']"
result2 = safe_eval(expression2, variables)
print(result2)	# Output: 3

expression3 = "a < b and z['a'] == 1"
result3 = safe_eval(expression3, variables)
print(result3)	# Output: True

expression4 = "not (a > b or z['b'] == 3)"
result4 = safe_eval(expression4, variables)
print(result4)	# Output: True

expression5 = "abs(-10) + len(x)"
result5 = safe_eval(expression5, variables)
print(result5)	# Output: 20

expression6 = "math.sqrt(16)"
result6 = safe_eval(expression6, variables)
print(result6)	# Output: 4.0

expression7 = "{'key1': 1, 'key2': 2}['key1'] + [1, 2, 3][1]"
result7 = safe_eval(expression7, variables)
print(result7)	# Output: 3

expression8 = "[i * 2 for i in range(5)]"
result8 = safe_eval(expression8, variables)
print(result8)	# Output: [0, 2, 4, 6, 8]

expression9 = "[i * 2 for i in range(5) if i % 2 == 0]"
result9 = safe_eval(expression9, variables)
print(result9)	# Output: [0, 4, 8]

expression10 = "[[i * j for j in range(3)] for i in range(3)]"
result10 = safe_eval(expression10, variables)
print(result10)	 # Output: [[0, 0, 0], [0, 1, 2], [0, 2, 4]]

expression11 = "3 if a < b else 4"
result11 = safe_eval(expression11, variables)
print(result11)	 # Output: 3

expression12 = "sorted([3, 1, 2])"
result12 = safe_eval(expression12, variables)
print(result12)	 # Output: [1, 2, 3]

expression13 = "list(reversed([1, 2, 3]))"
result13 = safe_eval(expression13, variables)
print(result13)	 # Output: [3, 2, 1]

expression14 = "list(map(lambda x: x * 2, [1, 2, 3]))"
result14 = safe_eval(expression14, variables)
print(result14)	 # Output: [2, 4, 6]

expression15 = "list(filter(lambda x: x % 2 == 0, [1, 2, 3, 4]))"
result15 = safe_eval(expression15, variables)
print(result15)	 # Output: [2, 4]

expression16 = "all([True, True, False])"
result16 = safe_eval(expression16, variables)
print(result16)	 # Output: False

expression17 = "any([False, False, True])"
result17 = safe_eval(expression17, variables)
print(result17)	 # Output: True

expression18 = "list(zip([1, 2], ['a', 'b']))"
result18 = safe_eval(expression18, variables)
print(result18)	 # Output: [(1, 'a'), (2, 'b')]

expression19 = "list(enumerate(['a', 'b', 'c']))"
result19 = safe_eval(expression19, variables)
print(result19)	 # Output: [(0, 'a'), (1, 'b'), (2, 'c')]

# Example with additional functions
additional_functions = {
	'custom_func': lambda x: x * 2
}
expression20 = "custom_func(5)"
result20 = safe_eval(expression20, variables, additional_functions)
print(result20)	 # Output: 10

# Example with bitwise inversion
expression21 = "~5"
result21 = safe_eval(expression21, variables)
print(result21)	 # Output: -6

# Example with math.pi
expression22 = "math.pi"
result22 = safe_eval(expression22, variables)
print(result22)	 # Output: 3.141592653589793

# Example with inline if assignment
expression23 = "x = 10 if a < b else 20"
safe_eval(expression23, variables)
print(variables['x'])  # Output: 10

# Example with walrus operator
expression24 = "(y := 10) + 5"
result24 = safe_eval(expression24, variables)
print(result24)	 # Output: 15
print(variables['y'])  # Output: 10

# Example with dictionary merging
expression25 = "{'a': 1} | {'b': 2}"
result25 = safe_eval(expression25, variables)
print(result25)	 # Output: {'a': 1, 'b': 2}

# Example with random functions
expression26 = "randrange(1, 10)"
result26 = safe_eval(expression26, variables)
print(result26)	 # Output: Random number between 1 and 9

expression27 = "choice(['apple', 'banana', 'cherry'])"
result27 = safe_eval(expression27, variables)
print(result27)	 # Output: Randomly chosen fruit from the list

# Example with short-circuiting
variables.update({'a': None, 'b': 7})
expression28 = "False if a is None else a if a < b else False"
result28 = safe_eval(expression28, variables)
print(result28)	 # Output: False

# Example with multiple variable assignment
expression29 = "a, b, c, d, e = 0, 1, 2, 3, 4"
safe_eval(expression29, variables)
print(variables['a'], variables['b'], variables['c'], variables['d'], variables['e'])  # Output: 0 1 2 3 4

# Example with walrus operator and multiple variable assignment
expression30 = "(a, b, c, d, e := 0, 1, 2, 3, 4)"
safe_eval(expression30, variables)
print(variables['a'], variables['b'], variables['c'], variables['d'], variables['e'])  # Output: 0 1 2 3 4

# Example with logical short-circuiting
variables.update({'A': False, 'B': True, 'C': 'Short-circuited'})
expression31 = "A and B or C"
result31 = safe_eval(expression31, variables)
print(result31)	 # Output: 'Short-circuited'
"""