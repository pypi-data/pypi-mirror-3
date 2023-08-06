import tweakdir
import Sablot
sp = Sablot.CreateProcessor()
sheet = open('sheet.xsl', 'r').read()
input = open('input.xml', 'r').read()
sp.run('arg:sheet', 'arg:input', 'arg:output', [], [('input', input), ('sheet', sheet)])
text = unicode(sp.getResultArg('output'), 'utf8')
print text.encode('ISO-8859-1')
