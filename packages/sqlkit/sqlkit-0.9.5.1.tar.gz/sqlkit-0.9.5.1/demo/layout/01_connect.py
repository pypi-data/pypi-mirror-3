"""Bricks/connect"""


simple_menu = """
 {  nome cognome
   indirizzo  -
   b=registra b=chiudi }

"""



l = Layout(simple_menu, opts="Vs")
w = l.show()

def di_ciao(*args):
    for i, val in enumerate(args):
        print i, val

def close_window(widget, window):
    print type(window)
    window.destroy()
    
l.connect(
    ('b=chiudi', 'clicked', close_window, w['Window']),
    ('b=registra', 'clicked', di_ciao, 'uno', 'due'),
    )

