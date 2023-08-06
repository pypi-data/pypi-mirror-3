"""more/scrolled

Simple example of a scrolled window. We use a 'cluster' of label/entry in a
table, in a view-port, in a scrolled Window
"""

lay = ""
for i in range(40):
    lay += " l=label%s e=label%s:10\n" % (i, i)

l = Layout("{S {p { %s}}}" % lay)
l.xml('/tmp/x.glade')
w = l.show()
