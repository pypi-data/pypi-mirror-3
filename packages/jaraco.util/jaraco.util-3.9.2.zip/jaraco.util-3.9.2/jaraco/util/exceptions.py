def throws_exception(callable, exception=Exception):
	"""
	Return True if the callable throws the specified exception
	
	>>> throws_exception(lambda: int('3'))
	False
	>>> throws_exception(lambda: int('a'))
	True
	>>> throws_exception(lambda: int('a'), KeyError)
	False
	"""
	try:
		callable()
	except exception:
		return True
	except Exception:
		pass
	return False
