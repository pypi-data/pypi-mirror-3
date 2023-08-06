#!/usr/local/bin/python
import tweakdir
from urlhandler import *
import os, Sablot
sp = Sablot.CreateProcessor()
print 'calling regHandler()'
sp.regHandler(Sablot.HLR_SCHEME, Urlschemehandler())
print 'reading sheet'
sheet = open('sheet.xsl', 'r').read()
url = 'file:' + os.path.join(os.getcwd(), 'input.xml')
url = 'http://localhost/input.xml'
sp.run('arg:sheet', url,
       'arg:output', [], [('sheet', sheet)])
text = unicode(sp.getResultArg('output'), 'utf8')
print text.encode('ISO-8859-1')
