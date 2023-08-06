"""Bricks/toolbar

toolbar example. I had to force a width to let the icons to be visible. Otherwise just an arrow would appear.
"""

lay = """
    {O.1 tb=gtk-save tb=gtk-delete tb=gtk-new tb=gtk-quit}
    {O.2 tb=gtk-save-as tb=gtk-file tb=gtk-zoom tb=gtk-zoom-fit}
    {O.3 tb=gtk-exit tb=gtk-no tb=gtk-ok tb=gtk-cut}
"""

l = Layout(lay)
l.prop('Window','width_request',300)
l.prop('O.1', 'toolbar_style','GTK_TOOLBAR_TEXT')
l.prop('O.2', 'toolbar_style','GTK_TOOLBAR_ICONS')
l.prop('O.3', 'toolbar_style','GTK_TOOLBAR_BOTH')
#l.xml('/tmp/a.glade')
w = l.show()
