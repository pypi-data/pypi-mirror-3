#!/usr/bin/python
# -*- coding: utf-8 -*-   -*- mode: python -*-

import sys
sys.path.append('../..')

from sqlkit.layout import Layout
import gtk

simple_menu = """
 {B m=_File  m=Produzione m=Commesse } -
 {N.uno
    {T.a cal=uno   -
      nome cognome
      indirizzo  -
      b=registra b=chiudi
      }
    TVS=due }

"""


l = Layout(simple_menu, opts="s")  # s for status bar
# tips written before show() are written in glade
l.tip('b=registra', 'Questo deve essere un nome')
l.elements['b=chiudi'].properties['use_stock'] = 'True'
l.elements['b=chiudi'].properties['label'] = 'gtk-cancel'
#l._dbg_show_objs()
l.notepad('N.uno',['Prima scheda', 'Seconda scheda'], "right")

# siccome nella definizione del layout il widget nome e` un combo
# sappiamo che viene scomposto in una entry e una label dunque basta
# passargli i singoli widget
l.tip("e=nome", "Questo è un tip per la entry nome")
l.tip("l=nome", "tip per la label")

l.tip("cal=uno", "Questo è un tip per il calendario")

l.xml('/tmp/sd.glade')   # we can write it to a file

w = l.show()
#w['T.a'].set_row_spacing(4, 20)
#sys.exit()

w['sb=StBar'].push(w['sb=StBar'].get_context_id('prova'),'Prima Prova')

# tips written after use gtk.Tooltip
l.tip('b=chiudi', 'Chiudi tutto')  

def di_ciao(*args):
    print 'ciao'

def nuovo_layout(*args):
    lay = """
         {B  m=Nobilitazione m=Subbiatura m=Commesse } {O b=tools}
         {h TVS=uno TXS=due} -
    """
    print "Ora un nuovo layout"
    new = Layout(lay,opts='s')
    new.show()
    new.sb('Seconda Prova')
    

l.menu('m=_File',
    ('_Fine' ,  'activate',  gtk.main_quit ),  # Normal
    ('inizio' , 'activate',  di_ciao, ),
    ('gtk-open' , 'activate', gtk.main_quit), # w/ stock image
    ('gtk-new' ,  'activate', nuovo_layout), # w/ stock image
    ('gtk-save' , 'activate', gtk.main_quit), # w/ stock image
    )   

l.sig(
    ('b=chiudi',lambda wid: gtk.main_quit(), 'clicked'),
#    ('l=nome',lambda wid: gtk.main_quit(), 'enter'),  # enter non esiste!
    )


gtk.main()
