"""Bricks/gtk.Layout


"""
import gtk

lay = """
   LS=a
"""

l = Layout(lay, opts="T")

w = l.show()
e = gtk.Entry()

def drag_begin_cb(*args):
    print 'BEGIN'
    
def drag_end_cb(*args):
    dbg.write('END')
    
def drag_motion_cb(*args):
    dbg.write('MOTION')
    

lay = w['Lay=a']
lay.connect("drag_begin", drag_begin_cb)
lay.connect("drag_end",   drag_end_cb)
lay.connect("drag_motion",drag_motion_cb)

w['Lay=a'].put(e, 50,50)
l.prop('Lay=a', 'width-request', 300)
l.prop('Lay=a', 'height-request', 300)
e.show()

