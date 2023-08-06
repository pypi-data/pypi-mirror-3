"""more/esempio logo
"""


lay =  """
   i=logo.jpg
   {B m=_Richieste }
   {B m=_Commesse  }
   {B m=_Articolo  }
"""

l = Layout(lay, title='Eurotex')
w = l.show()

l.menu('m=_Richieste',
       ('Nuova richiesta offerta', 'activate', lambda e: nuova()) )

l.menu('m=_Commesse',
       ('Inserimento commessa', 'activate', lambda e: nuova()),
       ('Pianificazione commesse', 'activate', lambda e: nuova())   )


l.menu('m=_Articolo',
       ('Progettazione Articolo', 'activate', lambda e: nuova()),
       ('Disegno Modelli', 'activate', lambda e: nuova()) )


