import tweakdir
import Sablot
sp = Sablot.CreateProcessor()
sheet = open('sheet4.xsl', 'r').read()
input = open('input.xml', 'r').read()

class MessageHandler:
    def makeCode(self, *args):
	print 'makeCode %s' % (args,)
    def log(self, *args):
	print 'log %s' % (args,)
    def error(self, *args):
	print 'error %s' % (args,)
MessageHandler().makeCode(1, 2, 3)
sp.regHandler(Sablot.HLR_MESSAGE, MessageHandler())
sp.run('arg:sheet', 'arg:input', 'arg:output', [], [('input', input), ('sheet', sheet)])
text = unicode(sp.getResultArg('output'), 'utf8')
res  = text.encode('ISO-8859-1')
