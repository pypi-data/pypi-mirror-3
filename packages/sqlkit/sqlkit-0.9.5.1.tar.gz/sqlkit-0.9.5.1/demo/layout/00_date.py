"""Bricks/date

uses dateedit a composed custom widget.

NOTE!!!! 
   Setting of properties is only
   garantied  after widget creation
"""

lay = """
    d=date1
    d=date2
"""

import datetime

l = Layout(lay)
w = l.show()

### NOTE: these settings must follow l.show()!!! 
date = datetime.datetime(2006, 01, 31)
l.prop('d=date1', 'date', date  )

o = w['d=date1']

