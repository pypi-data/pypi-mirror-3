import tweakdir
import Sablot
f = open("sheet.xsl","r")
g = open("input.xml","r")
print Sablot.processStrings(f.read(), g.read())
f.close()
g.close()


