"""Bricks/spinbutton


"""


simple_menu = """
   {O ts=limit tb=gtk-refresh }
   s=limit2

"""

def show(*args):
    global w
    w['s=limit'].update()
    print w['s=limit'].get_value()


l = Layout(simple_menu, opts="Ts")

w = l.show()
adj = w['s=limit'].get_adjustment()
adj.set_all(23,10,100,10,10,0)

l.connect(
    ('tb=gtk-refresh', 'clicked', show)
    )

    
