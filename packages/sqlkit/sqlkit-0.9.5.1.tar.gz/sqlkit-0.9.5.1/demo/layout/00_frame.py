"""Bricks/frames

An example of frame

"""


lay = """
   uno 
   {|T.table
      abra cadabra
      dumba balu
      } -
"""

import gtk

l = Layout(lay, opts="-")

w = l.show()
#w['F.table'].set_label('frame label')


        
    
