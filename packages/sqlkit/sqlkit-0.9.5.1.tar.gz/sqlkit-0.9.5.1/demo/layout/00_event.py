"""Bricks/event-label+entry"""


simple_menu = """
    nome
"""


l = Layout(simple_menu, opts="Ts-")
l.prop('Window', 'visible', True)

w = l.show()
def pressed(wdg, event):
    print "wdg: %s, ev: %s" % (wdg, event)

w['e=nome'].connect('key_press_event', pressed)
w['E=nome'].connect('button-press-event', pressed)

