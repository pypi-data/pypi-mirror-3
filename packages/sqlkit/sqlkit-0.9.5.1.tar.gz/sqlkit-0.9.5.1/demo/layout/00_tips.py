"""Bricks/tips"""


simple_menu = """
   { {B m=menu} {O tb=gtk-refresh }}
   { L=nome e=nome
   cognome r=due
   c=uno   r=tre/due }

"""



l = Layout(simple_menu, opts="Ts")

w=l.show()

l.tip('tb=gtk-refresh', 'toolbox nome...')
l.show()
l.tip('r=tre/due', "anche dopo")
l.tip('e=nome', 'nome...')
l.tip('E=nome', 'eventBox nome...')
l.tip('m=menu', "Anche sui menu")
l.tip('M=menu', "Anche sui Menu")
l.tip('r=due', "sui radio")
l.tip('c=uno', "e sui check")
