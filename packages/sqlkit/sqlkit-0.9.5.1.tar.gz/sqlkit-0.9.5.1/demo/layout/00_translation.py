"""Bricks/translation &amp; tips

You can write translations and tips in a separate file or a string, unique
for the whole application.

The first column sets the key, the second the label, the third the tip.
If you use a key w/o a specifier (e= part), it will be applied to all widgets
with that name. If both are present, the more specific apply.

"""



trad = """
nome	Nome proprio	Label doesn't show this text since it does not have sensitivity
e=nome	Nome	Label doesn't ...
l=cognome	il tuo cognome	Non vergognarti, scrivilo...
"""
layout.map_labels(buf=trad)


simple_menu = """
   nome cognome
   indirizzo  -
"""
l = Layout(simple_menu)

w = l.show()


