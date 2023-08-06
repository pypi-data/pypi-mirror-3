"""Bricks/toolbar singolo

toolbar example. I had to force a width to let the icons to be visible. Otherwise just an arrow would appear.
"""

lay = """
    {O tb=gtk-save tb=gtk-delete tb=gtk-new tb=gtk-quit}
"""

l = Layout(lay)
l.prop('Window','width_request',300)
#l.xml('/tmp/t.glade')
w = l.show()
