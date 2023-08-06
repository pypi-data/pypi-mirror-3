import sys

import gobject
import gtk
import pango

from sqlkit import debug as dbg
from cell_renderers import CellRendererVarchar

def unset_real_size(window, event):
    """Fields 'real width' and 'real height' become obsolete (or at least
    useless) when a resize actually takes place.
    """

    window.set_data('real width', None)
    window.set_data('real height', None)
    
    handler = window.get_data('configure handler')
    if handler:
        # The callback is now useless; remove it.
        window.disconnect(handler)
        window.set_data('configure handler', None)
    
def ensure_configure_handler(window):
    """Ensure that unset_real_size is called.
    """
    if not window.get_data('configure handler'):
        new_handler = window.connect('configure-event', unset_real_size)
        window.set_data('configure handler', new_handler)

def get_width(window):
    width = window.get_data('real width')
    if not width:
        width = window.get_size()[0]
    return width

def get_height(window):
    height = window.get_data('real height')
    if not height:
        height = window.get_size()[1]
    return height

def set_width(window, width):
    ensure_configure_handler(window)

    window.set_data('real width', width)

    height = get_height(window)        
    window.resize(width, height)
    
def set_height(window, height):
    ensure_configure_handler(window)

    window.set_data('real height', height)

    width = get_width(window)        
    window.resize(width, height)


def set_height_request(treeview, rows=None):
    """
    Show "rows" rows in the treeview,
    or a reasonable number if "rows" is not set.
    Untested with multiline rows.
    """

    if not rows:
        rows = len(treeview.get_model())
        if rows == 0:
            rows = 10
        if rows > 30:
            rows = 30

    column      = treeview.get_column(0)
    cell_height = column.cell_get_size()[4]
    if not cell_height:
        while gtk.events_pending():
            gtk.main_iteration()
        cell_height = column.cell_get_size()[4]
        
    spacing = treeview.style_get_property('vertical-separator')

    needed_height = cell_height * rows + (spacing) * (rows-1)
    top_widget = column.get_property('widget')
    if top_widget:
       top_height = top_widget.get_allocation().height
    else:
        top_height = cell_height
 
    needed_height += top_height

    dbg.write('needed', needed_height, 'spacing', spacing)

    treeview.set_property('height-request', needed_height)

    toplevel        = treeview.get_toplevel()
    visible_rect    = treeview.get_visible_rect()
    missing_height  = needed_height - visible_rect.height
    new_height      = toplevel.get_allocation().height + missing_height
#   print "toplevel:", toplevel, "old:", toplevel.get_allocation().height, "new:", new_height
    set_height(toplevel, new_height)
    
def get_string_exact_width(context, string):
    """
    (render and) Return width of a string in given context.
    """
    description = context.get_font_description()
    layout = pango.Layout(context)
    layout.set_text(string)
    width = layout.get_pixel_extents()[1][2]
    return width

def get_string_width(context, string=None, chars_num=80):
    """
    Find how much space is needed to render a string of "chars_num"
    characters in pango context "context". If "string" is given, compute this
    number exactly, actually recomputing rendering of the string.
    Otherwise, use the "approximate_chars_width" of the font.
    """
    if string != None:
        dbg.write("calculating width of", string[:chars_num], chars_num, type(string))
        return get_string_exact_width(context, string[:chars_num])
    else:
        # Perfection would imply setting this to actual language
        language = None
        description = context.get_font_description()
        metrics = context.get_metrics(description)
        # Pango uses its own internal measure unit. "pango.PIXELS" converts it.
        pango_width = metrics.get_approximate_char_width()*chars_num
        width = pango.PIXELS(pango_width)
        return width
        
def get_screen_width(effective = True):
    """
    Ugly hack. Couldn't find anything better. And in fact it's not strange,
    since GNOME HIGs apparently don't like this.
    """
    root = gtk.gdk.get_default_root_window()
    prop = gtk.gdk.atom_intern('_NET_WORKAREA')
    fields = root.property_get(prop)
    if sys.platform.startswith('win') or not fields:
        # Notice Windows will fallback here and assume there are no lateral panels.
        screen = root.get_screen()
        return screen.get_width()
    else:
        fields = root.property_get(prop)
        sizes = fields[2]
        if effective and sizes:
            width = sizes[2]
            return width

    
def set_optimal_width(treeview, max_pixels=None):
    """
    Set optimal width of the treeview, based on width request by cellrenderers.

    This means that the window containing the treeview is resized accordingly
    (with care taken not to exit screen limit, and anyway not making the
    treeview larger that max_pixels, if set).
    If called before the treeview is realized (and with "resize" set), this
    function assumes that there is nothing else on the right and on the left of
    the treeview (e.g. the the treeview is in a bare sqltable).
    If called after, it supposes that, if there is something on the left and on
    the right, the treeview and all its parents have horizontal expand property
    set.
    """    

    widget = treeview
    
    scrolledwindows = []
    scrolledwindows_policies = []
    scrolledwindows_hscrollbars = []
    
    while widget:
        # The ScrolledWindows stop propagation of queue_redraws, unless they
        # have the scrollbars disabled, so here we disable them...
        if gobject.type_is_a(widget, gtk.ScrolledWindow):
            scrolledwindows.append(widget)
            scrolledwindows_policies.append(widget.get_policy())
            widget.set_policy(gtk.POLICY_NEVER, gtk.POLICY_NEVER)
            scrolledwindows_hscrollbars.append(widget.get_hscrollbar())
        widget = widget.get_parent()

    toplevel = treeview.get_toplevel()

    # ... then we can take the size...

    new_width = toplevel.size_request()[0]

    # ... add the size of bars...
    bars_width = 0
    for index in range(len(scrolledwindows)):
        # (not needed if the policy hides it)
        if scrolledwindows_policies[index][0] == gtk.POLICY_ALWAYS:
            bars_width += scrolledwindows_hscrollbars[index].size_request()[0]
        scrolledwindows[index].set_policy(*scrolledwindows_policies[index])
#    print "width:", new_width

    # ... and put together the total size.

    new_width += bars_width
 
    available = get_screen_width()
    
    if toplevel.window:
        allocation = toplevel.window.get_frame_extents()
        border = allocation.width - get_width(toplevel)
#        print "border", border
    else:
        # Guess (Ubuntu's metacity's default theme and settings)
        border = 10

    extra = new_width + border - available 

    if extra > 0:
        new_width -= extra
#        print "extra", extra
        

    set_width(toplevel, new_width)
    return
 
def zoom_to_fit(treeview, resize=True):
    """Take a treeview (presumably from a sqlmask) and, for each column asking
    a fixed size, reset space request criterion to content only (not database
    lenght introspection).
    Then, if "resize" is True, resize window accordingly.
    """
    columns = treeview.get_columns()
    for column in columns:
        renderers = column.get_cell_renderers()
        for renderer in renderers:
            if hasattr(renderer, 'fixed_width') and renderer.fixed_width:
                # Let's fall back to the usual size method...
                renderer.fixed_width = False
        column.set_expand(True)
        column.set_min_width(0)

    if resize:
        set_optimal_width(treeview)
        
    treeview.columns_autosize()

def set_all_nonfilling(wid, level):
    """
    Set all widgets under the same toplevel as "wid" as non filling and non
    expanding (where this packing property has sense).
    """
    if not level or not wid:
        return
    try:
        if wid.seen:
            return
    except:
        pass
#    print "browsed to", wid
    next_level = []
    try:
        parent = wid.get_parent()
        if hasattr(parent, 'child_set_property'):
            try:
                parent.child_set_property(wid, 'expand', False)
                parent.child_set_property(wid, 'fill', False)
            except:
                pass
            try:
                import gtk
                parent.child_set_property(wid, 'y-options', None)
            except:
                pass
        next_level.append(wid.get_parent())
    except:
        pass
    try:
        for child in wid.get_children():
            next_level.append(child)
    except:
        pass
    wid.seen = True
     

    for other in next_level:
        set_all_nonfilling(other, level-1)

def set_this_filling(wid):
    """
    Set all widgets over (parents, or grandparents... of) wid as filling and
    expanding (where those packing properties make sense).
    """
    while wid:
        newwid = wid.get_parent()
        if gobject.type_is_a(wid, gtk.Alignment):
            wid.set_property('yscale',1)
            dbg.write("setting yscale:", wid)
        if gobject.type_is_a(newwid, gtk.Table):
            newwid.child_set_property(wid, 'y-options', gtk.FILL|gtk.EXPAND)
            dbg.write("setting y-options:", wid)
        wid = newwid

def print_debug(wid):
    """
    Print debug information about packing of a widget and its superiors.
    """
    dbg.write("starting with", wid)
    number = 1 
    while wid:
        newwid = wid.get_parent()
        number += 1
        dbg.write("number", number, ":", newwid)
        try:
            dbg.write(newwid.get_property('xscale'), newwid.get_property('yscale'), "alignment")
            print "changing"
        except:
            pass
        try:
            dbg.write(newwid.get_allocation().width, newwid.get_allocation().height)
        except:
            pass
        try:
            dbg.write(newwid.get_property('n-rows'), newwid.get_property('n-columns'))
            dbg.write(newwid.child_get_property(wid, 'left-attach'), newwid.child_get_property(wid, 'top-attach'), newwid.child_get_property(wid, 'right-attach'), newwid.child_get_property(wid, 'bottom-attach'))
            dbg.write(newwid.get_children())
        except:
            pass
        wid = newwid

