"""Bricks/toolbutt calendar

icons can be added directly to the IconFactory and called as a normal stock
image as in tb=cal

I Have not understood how to use themes, thought
"""
import os
from sqlkit import layout
from sqlkit.layout import misc

icon_path = os.path.join( os.path.dirname(layout.__file__), 'cal15.png')
misc.add_stock_icons()

lay = """
   {O tb=sk-calendar tb=gtk-new }
   l=esempio_calendario
"""

l=Layout(lay)
w = l.show()

