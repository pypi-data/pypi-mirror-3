import multiprocessing

def f(foo, bar=None):
	result = foo + bar if bar else foo
	return result, bar is not None

def pool_in_globals():
	return 'pool' in globals()

def process_name():
	return multiprocessing.current_process().name

pool = multiprocessing.Pool(1)

class MyClass(object):

	def do_it(self):
		args = [3,4]
		kwargs = dict()
		print 'result is', pool.apply(f, args, kwargs)
		print 'result is', pool.apply(f, [3])
		try:
			print 'result is', pool.apply(f, [3,'x'])
		except TypeError:
			print 'type error'
		print 'pool_in_globals() ->', pool.apply(pool_in_globals, [])
		print 'process name in main:', process_name()
		print 'process name in child:', pool.apply(process_name)

if __name__ == '__main__':
	o = MyClass()
	o.do_it()
