"""Scheme handler class for the Sablotron Python module (version 0.3)
November 4, 2000, Günter Radestock"""

import urllib, Sablot

class Urlschemehandler:
    def __init__(self):
	self.handles = []
	
    def getAll(self, scheme, rest, bytecount):
	print 'getall', scheme, rest, bytecount
	#raise Sablot.SchemeHandlerError, Sablot.SH_ERR_UNSUPPORTED_SCHEME
	url = scheme + ':' + rest
	return urllib.urlopen(url).read()

    def open(self, scheme, rest):
	print 'open', scheme, rest
	#raise Sablot.SchemeHandlerError, Sablot.SH_ERR_UNSUPPORTED_SCHEME
	handle = self.gethandle()
	url = scheme + ':' + rest
	self.handles[handle] = urllib.urlopen(url)
	return handle
    
    def get(self, handle, bytecount):
	print 'get'
	return self.handles[handle].read(bytecount)

    def put(self, handle, buffer):
	print 'put', handle, len(buffer)
	pass

    def close(self, handle):
	print 'close', handle
	self.handles[handle] = None

    def gethandle(self):
	try:
	    return self.handles.index(None)
	except ValueError:
	    self.handles.append(None)
	    return len(self.handles) - 1
