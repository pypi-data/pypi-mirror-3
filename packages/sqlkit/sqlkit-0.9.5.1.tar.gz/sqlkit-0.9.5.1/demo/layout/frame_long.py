#!/usr/bin/python
# -*- coding: utf-8 -*-   -*- mode: python -*-

import sys
sys.path.append('../..')

from layout import Layout
import gtk

simple_menu = """
 {F.gen {  nome cognome
           indirizzo }
 }
 {F.2gen {  sesso   eta
            scuola  classe }
 }
 {F.misc {  altezza piedi
            hobby   - }
 }
"""


l = Layout(simple_menu, opts="Vs")  # s for status bar
l.frame('F.gen',['Generalita',], "left")
l.frame('F.2gen',['Altre banalita',], "left")
l.frame('F.misc',['Amenita',], "left")

w = l.show()
