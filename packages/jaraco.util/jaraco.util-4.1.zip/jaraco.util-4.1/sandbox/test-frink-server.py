import xmlrpclib

proxy = xmlrpclib.ServerProxy("http://localhost:8000/")

def frink(string):
	result = proxy.parse(string)
	print 'frink says %(string)s is %(result)s' % vars()

frink('2+2')
frink('2+x')
frink('F[C[35]]')