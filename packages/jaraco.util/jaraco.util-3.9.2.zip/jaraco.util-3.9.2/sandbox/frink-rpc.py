import sys
from SimpleXMLRPCServer import SimpleXMLRPCServer

sys.path.append(r'c:\users\jaraco\downloads\frink.jar')

from frink.parser import Frink

f = Frink()

server = SimpleXMLRPCServer(('', 8000))
print "Listening on port 8000..."
server.register_function(f.parseString, "parse")
server.serve_forever()
