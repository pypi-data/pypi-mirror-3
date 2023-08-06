#!/usr/local/bin/python
import tweakdir
import os, Sablot
from Sablot.urlhandler import *
sp = Sablot.CreateProcessor()
print 'calling regHandler()'
sp.regHandler(Sablot.HLR_SCHEME, Urlschemehandler())

class TestMiscHandler:
    def documentInfo(self, ctype, enc):
	print 'ContentType=%s, Encoding=%s' % (ctype, enc)
sp.regHandler(Sablot.HLR_MISC, TestMiscHandler())

print 'reading sheet'
sheet = open('sheet.xsl', 'r').read()
url = 'file:' + os.path.join(os.getcwd(), 'input.xml')
url = 'http://localhost/input.xml'
sp.run('arg:sheet', url,
       'arg:output', [], [('sheet', sheet)])
text = unicode(sp.getResultArg('output'), 'utf8')
print text.encode('ISO-8859-1')
