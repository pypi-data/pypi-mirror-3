#!/usr/bin/python
# -*- coding: utf-8 -*-   -*- mode: python -*-

import sys
sys.path.append('../..')

from layout import Layout

simple_menu = """
 {|.gen nome cognome
           indirizzo }
 {|.2gen  { l=sesso
            r=m/sesso r=f/sesso }  s=eta
            scuola  C=classe }
 {|.misc  altezza piedi
            hobby   - }

"""

a = """

"""

l = Layout(simple_menu, opts="Vs")  # s for status bar
l.frame('F.gen',['Generalita',], "right")
l.frame('F.2gen',['Altre banalita',], "left")
l.frame('F.misc',['Amenita',], "left")

l.elements['C=classe'].properties['items'] = "1a\n2a\n3a"
#l.xml('/tmp/sd.glade')   # we can write it to a file
w = l.show()

