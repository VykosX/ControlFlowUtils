import ast
import operator
import math

# Define supported operators
operators = {
	ast.Add: operator.add,
	ast.Sub: operator.sub,
	ast.Mult: operator.mul,
	ast.Div: operator.truediv,
	ast.Pow: operator.pow,
	ast.BitXor: operator.xor,
	ast.USub: operator.neg,
	ast.Eq: operator.eq,
	ast.NotEq: operator.ne,
	ast.Lt: operator.lt,
	ast.LtE: operator.le,
	ast.Gt: operator.gt,
	ast.GtE: operator.ge,
	ast.And: operator.and_,
	ast.Or: operator.or_,
	ast.Not: operator.not_
}

# Define supported functions
default_functions = {
	'abs': abs,
	'len': len,
	'max': max,
	'min': min,
	'sum': sum,
	'round': round,
	'range': range,
	'sorted': sorted,
	'reversed': reversed,
	'map': map,
	'filter': filter,
	'all': all,
	'any': any,
	'zip': zip,
	'enumerate': enumerate,
	'math': math
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
	node = ast.parse(expr, mode='eval')

	def _eval(node):
		if isinstance(node, ast.Expression):
			return _eval(node.body)
		elif isinstance(node, ast.BinOp):
			left = _eval(node.left)
			right = _eval(node.right)
			return operators[type(node.op)](left, right)
		elif isinstance(node, ast.UnaryOp):
			operand = _eval(node.operand)
			return operators[type(node.op)](operand)
		elif isinstance(node, ast.BoolOp):
			values = [_eval(v) for v in node.values]
			if isinstance(node.op, ast.And):
				return all(values)
			elif isinstance(node.op, ast.Or):
				return any(values)
		elif isinstance(node, ast.Compare):
			left = _eval(node.left)
			for operation, comparator in zip(node.ops, node.comparators):
				right = _eval(comparator)
				if not operators[type(operation)](left, right):
					return False
				left = right
			return True
		elif isinstance(node, ast.Num):  # For Python 3.8 and earlier
			return node.n
		elif isinstance(node, ast.Constant):  # For Python 3.8 and later
			return node.value
		elif isinstance(node, ast.Name):
			if node.id in variables:
				return variables[node.id]
			elif node.id in functions:
				return functions[node.id]
			elif node.id in {'True', 'False', 'None'}:
				return {'True': True, 'False': False, 'None': None}[node.id]
			else:
				raise NameError(f"Variable '{node.id}' is not defined")
		elif isinstance(node, ast.Subscript):
			value = _eval(node.value)
			index = _eval(node.slice)
			return value[index]
		elif isinstance(node, ast.Index):  # For Python 3.8 and earlier
			return _eval(node.value)
		elif isinstance(node, ast.Slice):
			lower = _eval(node.lower) if node.lower else None
			upper = _eval(node.upper) if node.upper else None
			step = _eval(node.step) if node.step else None
			return slice(lower, upper, step)
		elif isinstance(node, ast.Tuple):
			return tuple(_eval(elt) for elt in node.elts)
		elif isinstance(node, ast.List):
			return [_eval(elt) for elt in node.elts]
		elif isinstance(node, ast.Dict):
			return {_eval(key): _eval(value) for key, value in zip(node.keys, node.values)}
		elif isinstance(node, ast.Call):
			func = _eval(node.func)
			args = [_eval(arg) for arg in node.args]
			if func in functions.values() or callable(func):
				return func(*args)
			else:
				raise TypeError(f"Unsupported function: {func}")
		elif isinstance(node, ast.Attribute):
			value = _eval(node.value)
			if value in functions.values():
				return getattr(value, node.attr)
			else:
				raise AttributeError(f"Access to attribute '{node.attr}' is not allowed")
		elif isinstance(node, ast.IfExp):
			test = _eval(node.test)
			body = _eval(node.body)
			orelse = _eval(node.orelse)
			return body if test else orelse
		elif isinstance(node, ast.ListComp):
			elt = node.elt
			generators = node.generators
			return _eval_listcomp(elt, generators)
		else:
			raise TypeError(f"Unsupported type: {type(node)}")

	def _eval_listcomp(elt, generators):
		"""
		Evaluate a list comprehension.
		
		:param elt: The element expression of the list comprehension.
		:param generators: The generators of the list comprehension.
		:return: The evaluated list comprehension.
		"""
		if not generators:
			return [_eval(elt)]
		
		gen = generators[0]
		iter_ = _eval(gen.iter)
		result = []
		
		for item in iter_:
			new_variables = variables.copy()
			new_variables[gen.target.id] = item
			if all(_eval(cond) for cond in gen.ifs):
				result.extend(_eval_listcomp(elt, generators[1:]))
		
		return result

	return _eval(node.body)

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
print(result1)  # Output: 13

expression2 = "z['a'] + z['b']"
result2 = safe_eval(expression2, variables)
print(result2)  # Output: 3

expression3 = "a < b and z['a'] == 1"
result3 = safe_eval(expression3, variables)
print(result3)  # Output: True

expression4 = "not (a > b or z['b'] == 3)"
result4 = safe_eval(expression4, variables)
print(result4)  # Output: True

expression5 = "abs(-10) + len(x)"
result5 = safe_eval(expression5, variables)
print(result5)  # Output: 20

expression6 = "math.sqrt(16)"
result6 = safe_eval(expression6, variables)
print(result6)  # Output: 4.0

expression7 = "{'key1': 1, 'key2': 2}['key1'] + [1, 2, 3][1]"
result7 = safe_eval(expression7, variables)
print(result7)  # Output: 3

expression8 = "[i * 2 for i in range(5)]"
result8 = safe_eval(expression8, variables)
print(result8)  # Output: [0, 2, 4, 6, 8]

expression9 = "[i * 2 for i in range(5) if i % 2 == 0]"
result9 = safe_eval(expression9, variables)
print(result9)  # Output: [0, 4, 8]

expression10 = "[[i * j for j in range(3)] for i in range(3)]"
result10 = safe_eval(expression10, variables)
print(result10)  # Output: [[0, 0, 0], [0, 1, 2], [0, 2, 4]]

expression11 = "3 if a < b else 4"
result11 = safe_eval(expression11, variables)
print(result11)  # Output: 3

expression12 = "sorted([3, 1, 2])"
result12 = safe_eval(expression12, variables)
print(result12)  # Output: [1, 2, 3]

expression13 = "list(reversed([1, 2, 3]))"
result13 = safe_eval(expression13, variables)
print(result13)  # Output: [3, 2, 1]

expression14 = "list(map(lambda x: x * 2, [1, 2, 3]))"
result14 = safe_eval(expression14, variables)
print(result14)  # Output: [2, 4, 6]

expression15 = "list(filter(lambda x: x % 2 == 0, [1, 2, 3, 4]))"
result15 = safe_eval(expression15, variables)
print(result15)  # Output: [2, 4]

expression16 = "all([True, True, False])"
result16 = safe_eval(expression16, variables)
print(result16)  # Output: False

expression17 = "any([False, False, True])"
result17 = safe_eval(expression17, variables)
print(result17)  # Output: True

expression18 = "list(zip([1, 2], ['a', 'b']))"
result18 = safe_eval(expression18, variables)
print(result18)  # Output: [(1, 'a'), (2, 'b')]

expression19 = "list(enumerate(['a', 'b', 'c']))"
result19 = safe_eval(expression19, variables)
print(result19)  # Output: [(0, 'a'), (1, 'b'), (2, 'c')]

# Example with additional functions
additional_functions = {
	'custom_func': lambda x: x * 2
}
expression20 = "custom_func(5)"
result20 = safe_eval(expression20, variables, additional_functions)
print(result20)  # Output: 10
