"""more/Entry e menu"""


simple_menu = """
 { {B m=_File  m=Produzione m=Commesse }  {O tb=gtk-close   } }
 {  nome cognome
   indirizzo  -
   { l=address e=address }
   b=registra b=chiudi }

"""



l = Layout(simple_menu, opts="Vs")
l.tip('b=registra', 'Questo deve essere un nome')


w = l.show()
l.tip('b=chiudi', 'Chiudi tutto')  
def di_ciao(*args):
    for i, val in enumerate(args):
        print i, val



l.menu('m=_File',
    ('fine' , 'activate', gtk.main_quit),
    ('inizio' , 'activate', di_ciao, ),
    ('gtk-open' , 'activate', gtk.main_quit, )
    )   

#print l.elements.keys
l.connect(
    ('b=chiudi', 'clicked', gtk.main_quit),
    ('b=registra', 'clicked', di_ciao, 'uno', 'due'),
    )

