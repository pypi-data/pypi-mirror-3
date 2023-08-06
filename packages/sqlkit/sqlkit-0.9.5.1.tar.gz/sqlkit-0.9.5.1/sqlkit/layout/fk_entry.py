"""
An entry with an arrow. Similar to comboBoxEdit but with possibility to
connect to click on the arrow

"""
import gobject
import gtk

from sqlkit import _

if gtk.gtk_version >= (2, 16):

    class FkEdit(gtk.Entry):
        __gtype_name__ = 'FkEntry'

        __gsignals__ = {
            'completion-requested' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                           (gobject.TYPE_PYOBJECT,)),                          
        }


        def __init__(self):
            gtk.Entry.__init__(self)
            self.props.secondary_icon_stock = 'gtk-find'
            self.props.secondary_icon_tooltip_text = _(
                "Find allowed values (Control-Enter/Shift-Enter)")
            #self.props.secondary_icon_stock = None
            self.connect('icon-press', self.icon_press_cb)

        def icon_press_cb(self, entry, icon_pos, event):
            self.emit('completion-requested', event)

else:

    class FkEdit(gtk.HBox):
        __gtype_name__ = 'FkEntry'

        __gsignals__ = {
            'completion-requested' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                           (gobject.TYPE_PYOBJECT,)),                          
        }

        def __init__(self):
            gtk.HBox.__init__(self)
            self.entry = gtk.Entry()

            # the date button
            self.button = gtk.Button()

            self._align_entry = gtk.Alignment(1,0,1,0)
            self._align_arrow = gtk.Alignment(0,0,0,0)

            self._align_entry.add(self.entry)
            self._align_arrow.add(self.button)

            self.add(self._align_entry)
            self.add(self._align_arrow)
            # the down arrow
            arrow = gtk.Arrow(gtk.ARROW_DOWN, gtk.SHADOW_OUT)
            self.button.add(arrow)
            arrow.show()
            # finally show the button
            self._align_entry.show_all()
            self._align_arrow.show_all()

            self.button.connect('button-press-event', self.button_press_cb)


            self.connect('realize', self.set_packing)

        def button_press_cb(self, button, event):
            self.emit('completion-requested', event)

        def modify_base(self, state, color):
            self.entry.modify_base(state, color)

        def set_packing(self, other):
            parent = self.get_parent()
            props = [prop.name for prop in parent.list_child_properties()]
            if 'y-options' in props:
                parent.child_set_property(self, 'y-options', 0)


