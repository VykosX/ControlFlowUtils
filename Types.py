class AnyType(str):
	def __ne__(self, __value: object) -> bool:
		return False

"""
class TautologyStr(str):
	def __ne__(self, other):
		return False

class ByPassTypeTuple(tuple):
	def __getitem__(self, index):
		if index>0:
			index=0
		item = super().__getitem__(index)
		if isinstance(item, str):
			return TautologyStr(item)
		return item
"""