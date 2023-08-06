# Copyright (C) 2009-2010, Sandro Dentella <sandro@e-den.it>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Classes that implement creation of column and cell renderers
This should allow to be as generic as possible while adding new renderers

Each Column widget need a 'master' argument that is the SqlWidget
in editing_started_cb and  edited_cb to set state variables on SqlWidget

.. autoclass:: View
   :members: add_column, select_path, start_editing

"""


import gtk
import gobject
import pango
from decimal import Decimal

import cell_renderers, utils as tv_utils
from sqlkit import debug as dbg, _, exc, fields
from sqlkit.layout import widgets
from sqlkit.misc.utils import str2list
from sqlkit.db.utils import DictLike

COLUMN_MENU = '''
<popup name="TreePopup">
  <placeholder name="Columns">
    <separator name="sep_cols" />
    <menuitem action="ExportView" />
    <menuitem action="Zoom-fit" />
    <menu action="ShowColumns" />
    <menu action="HideColumns" />
  </placeholder>
</popup>
'''


LBL_HOOVER_STYLE = gtk.gdk.color_parse('red')
class GenericColumn(object):
    RENDERER = gtk.CellRendererText
    RESIZE = True
    REORDER = True
    CLICK = True
    EXPAND = True
    MIN_DEFAULT_WIDTH = 4
    MAX_DEFAULT_WIDTH = 30
    PROPERTY = 'text'
    editable = False
    __metaclass__ = None if not dbg.debug else dbg.LogTheMethods

    
    def __init__(self, master, field_name, title, field=None):
        """
        Generic column with cell render setup

        :param master: the SqlWidget or which this Column is created, maybe a SqlMask if
                       the Column is created for FilterPanel
        :param field_name: the field_name used to add the field_name into master.gui_fields
        :param title: the title used for the column
        :param field: the field (if missing is looked for in master.gui_fields[field_name]
        """
        self.master = master
        if not field:
            field = self.master.gui_fields[field_name]
        self.field = field
        self.title  = title
        self.field_name = field_name
        self.column = self.setup_column(title)
        cell = self.setup_cell_renderers()
        self.column.set_cell_data_func(cell, self.cell_data_func_cb, self.PROPERTY) 
        self.column.cells_data_func = [(cell, self.cell_data_func_cb, self.PROPERTY) ]

    def setup_column(self, title):
        """
        setup column 
        """
        
        column = gtk.TreeViewColumn(title.replace('_',' '))
        column.set_data('field_name', self.field_name)  # used when reordering columns
        column.set_resizable(self.RESIZE)
        column.set_expand(self.EXPAND)
        column.set_reorderable(self.REORDER)
        column.set_clickable(self.CLICK)
        
        column.set_expand(self.is_expandable())
        column.connect('clicked', self.clicked_cb)
        self.add_header_widget(column)
        return column

    def setup_cell_renderers(self, cell_renderer=None):
        """
        setup cell renderers 
        """

        cell = cell_renderer or self.RENDERER()
        self.column.pack_start(cell, True)
        self.cell_set_property(cell)

        
        ## connect
        cell.connect('edited', self.edited_cb)
        cell.connect('editing-started', self.editing_started_cb)
        cell.connect('editing-canceled', self.editing_canceled_cb)

        return cell

### callback
    def edited_cb(self, cell, path, new_text):
        """
        callback on signal 'edited' on cell_renderer. 
        
        """
        ## NOTE: modelstore.clear will trigger text_edited_cb!!!
        if self.master.deleting_row:
            return True

        if self.master.edited_row_model_path is None:
            return True

        if self.master.cell_entry and self.master.cell_validate():
            self.master.cell_entry = None
            self.on_activate()
        else:
            return True

    def editing_started_cb(self, cell, editable, path):

        self.master.currently_edited_field_name = self.field_name
        self.master.initialize_record_editing(path)
        return True
    
    def cell_data_func_cb(self, column, cell, model, iter, prop_name):
        """
        function set by set_cell_data_func
        gets the attribute from the record and returns it
        """

        if not column.get_visible():
            return
        obj = model.get_value(iter, 0) 
        ## when the column is not representing a db-column (eg. is a python function)
        ## we pass the object itself to the function
        if self.field.persistent:
            value = getattr(obj, self.field_name)
        else:
            value = obj
            if isinstance(obj, self.master.mapper.class_):
                value = self.field.clean_value(value)

        cell.set_property('visible', True)        

        ## DB RECORDS
        if isinstance(obj, self.master.mapper.class_):
            cell.set_property('visible', True)        
            formatted_value = self.field.format_value(value)
            cell.set_property(prop_name, formatted_value)        
            cell.set_property('foreground-set', False)
            cell.set_property('cell-background-set', False)
            cell.set_property('editable', self.editable)

        ## TOTALS
        elif hasattr(self.master, 'totals') and isinstance(obj, self.master.totals.total_class):
            if self.field_name in self.master.totals.totals:
                if self.field.persistent:
                    formatted_value = self.field.format_value(value)
                    obj.set_value_and_colors(cell, formatted_value, self.field_name)
                else:
                    value = getattr(obj, self.field_name, None)
                    obj.set_value_and_colors(cell, self.field.format_value(value), self.field_name)
            else:
                cell.set_property('visible', False)
                    
            cell.set_property('editable', False)        

        ## HEADERS
        else:
            cell.set_property(prop_name, value)
            cell.set_property('editable', False)

    def editing_canceled_cb(self, widget):
        """
        clean-up of cell_entry and restore value
        """

        if self.master.cell_entry and self.master.cell_entry.substitute:
            # assigning a value to modelstore, triggers 'editing-canceled'
            self.master.cell_entry.substitute = False
            return
        
        self.master.set_value(self.field_name, self.field.initial_value)
        self.master.cell_entry = None

        self.master.sb(_("Editing canceled. Restoring original value"), seconds=3)
        
        
    def editable_connects(self, editable):
        """
        add here possible connect
        """
        editable.connect('activate', self.on_activate)
        return

    def on_activate(self, editable=None):
        # this is no longer connected to 'activate' signal since I prefere the changed value
        # be available. I prefere to keep similarity with what happens in a normal
        # entry where 'activate' means "press Enter". Pressing enter here make it edited.
        # That means it will also be triggered via Tab...
        self.master.run_hook('on_activate', self.field, field_name=self.field_name)
        
    def clicked_cb(self, column):
        """
        popup the menu on the header of the column
        """
        event =   gtk.gdk.Event(gtk.gdk.BUTTON_PRESS)
        event.button = 1
        treeview = column.get_tree_view()
        view = treeview.get_data('view')
        view.menu.popup_col_menu(event, treeview, self.field_name)
        
        return True
    
    

#### auxiliary
    def set_editable(self, editable):
        """
        set cells of this column editable or not

        :param editable: boolean
        """
        self.editable = editable 
        for cell in self.column.get_cell_renderers():
            cell.set_property('editable', editable)

    def cell_set_property(self, cell):
        """
        set cell properties
        """
        
        if self.field.editable and 'u' in self.master.mode:
            self.set_editable(True)
            cell.set_property('editable-set', True)
        else:
            cell.set_property('editable', False)
                
    def add_header_widget(self, column):
        """
        Add a header that accepts tooltips and bold labels for mandatory columns
        """
        # Label
        label_text, help_text = self.master.label_map.get(self.field_name, (None, None))
        label_text = self.master.get_label(label_text or self.title)
        label = gtk.Label()
        label.set_markup(label_text)

        ## bold italic
        if self.field.persistent and not self.field.nullable and not self.field.default:
                label.set_markup('<b><i>%s</i></b>' % label_text)

        # Tooltip
        if help_text:
            label.set_tooltip_text(help_text)

        # Header
        column.set_widget(label)
        label.show()

    def realize_cb(self, widget):
        watch = gtk.gdk.Cursor(gtk.gdk.HAND2)
        widget.window.set_cursor(watch)

    def is_expandable(self):
        """
        make expandable only Strings with n_chars > 20 or Text
        """
        #        if self.master.is_text(self.field_name):
        if isinstance(self.field, fields.TextField):
            return True
        if isinstance(self.field, fields.VarcharField):
            #if self.master.mapper_info.fields[self.field_name]['length'] > 20:
            if self.field.length and self.field.length > 20:
                return True
        return False

    def get_width(self):
        """
        Find the width looking in default database info or in col_width
        """

        if self.master.col_width and self.field_name in self.master.col_width:
            width = self.master.col_width.get(self.field_name, )
        else:
            width = self.field.length

            if not width or width < self.MIN_DEFAULT_WIDTH:
                width = self.MIN_DEFAULT_WIDTH

            if width > self.MAX_DEFAULT_WIDTH:
                width = self.MAX_DEFAULT_WIDTH

        return width

    

    def __repr__(self):
        return "<%s: %s >" % (self.__class__.__name__, self.field_name)

class BooleanColumn(GenericColumn):
    RENDERER = gtk.CellRendererToggle
    RESIZE = False
    EXPAND = False

    def set_editable(self, editable):
        """
        set cells of this column editable or not

        :param editable: boolean
        """
        self.editable = editable
        for cell in self.column.get_cell_renderers():
            cell.set_property('activatable', editable)

    def setup_cell_renderers(self, cell_renderer=None):
        """
        setup different cell_cb according to nullable value
        """

        cell = cell_renderer or self.RENDERER()
        self.cell_set_property(cell)

        self.column.pack_start(cell, True)
        self.column.set_data('cell', cell)
        
        ## connect
        cell.connect('editing-canceled', self.editing_canceled_cb) # ???
        cell.connect('toggled', self.toggled_signal_cb, self.master.modelproxy.modelstore)
            
        self.column.set_cell_data_func(cell, self.cell_data_func_cb)
        self.column.cells_data_func = [(cell, self.cell_data_func_cb)]
        cell.fixed_width = True
        return  cell
        
    def cell_set_property(self, cell):

        if self.field.editable:
            self.set_editable(True)
        else:
            self.set_editable(False)

    def toggled_signal_cb(self, cell, path, model):
        """
        callback that cicle into True/False/(inconsistent if nullable)
        """

        self.master.currently_edited_field_name = self.field_name
        self.master.initialize_record_editing(path)

        obj = self.master.modelproxy.modelstore[path][0]
        status = getattr(obj, self.field_name)

        if self.field.nullable:
            # status may be True/False/None - I want to cicle
            if   status == True:    status = False
            elif status == False:   status = None
            elif status == None:    status = True
        else:
            status = not status

        #self.field.set_value(status, initial=False, obj=obj)
        self.master.set_value(self.field_name, status, initial=False)
            
        return True
    
    def cell_data_func_cb(self, column, cell, model, iter, prop_name):
        """
        function set by set_cell_data_func for nullable boolean
        """

        if not column.get_visible():
            return
        
        obj = model.get_value(iter, 0) 
        value = getattr(obj, self.field_name)

        ## DB RECORDS
        if isinstance(obj, self.master.mapper.class_):
            cell.set_property('active', value)        
            cell.set_property('visible', True)       
            cell.set_property('activatable', self.editable)

            if value is None:
                cell.set_property('inconsistent', True)
            else:    
                cell.set_property('inconsistent', False)

        ## TOTALS
        elif isinstance(obj, self.master.totals.total_class):
            cell.set_property('visible', False)        
            cell.set_property('activatable', False)        
        
class VarcharColumn(GenericColumn):
    """
    A renderer that expands only large fields and that centers text if it's little
    Cell renderer is choosen according to VarChar or Text
    """
    __metaclass__ = dbg.LogTheMethods
    
    def setup_cell_renderers(self, cell_renderer=None):

        width = self.get_width()

        ## look for a possibly defined width
        ## choose cell renderer
        if width:
            cell = cell_renderers.CellRendererVarchar(width)
            cell.fixed_width = True
        else:
            cell = gtk.CellRendererText()

        GenericColumn.setup_cell_renderers(self, cell_renderer=cell)
        cell.set_property('ellipsize', pango.ELLIPSIZE_END)
        cell.set_data('width', width)
        
        self.set_alignment(cell)
        return cell

    def set_alignment(self, cell):
        """
        Set alignment of text in the cell
        """
        
        if self.field.length:
            try:
                ## if field has less then 4 chars, position it in the middle
                if int(self.field.length) <= 4:
                    cell.set_property('xalign', 0.5)
            except:
                pass
        return  cell


    def editing_started_cb(self, cell, editable, path):
        """
        prepare the editable, completion and validation
        """
        
        self.master.currently_edited_field_name = self.field_name
        self.master.cell_entry = CellEntry(editable, cell, path, self.field_name)
        editable.connect('remove-widget', self.remove_widget_cb)
        editable.connect('key-press-event', self.master.keypress_event_cb)
        editable.connect('focus-out-event', self.focus_out_cb, cell, path)
        self.editable_connects(editable)
        
        self.master.fkey_value = editable.get_text()

        if hasattr(self.master.field_widgets[self.field_name], 'completion'):
            completion = self.master.field_widgets[self.field_name].completion
            #if completion and not self.master.is_text(self.field_name):
            if completion and not isinstance(self.field, fields.TextField):
                completion.add_completion(editable)
                completion.add_callbacks(editable)
            
        ## MAX LENGTH: not enforce for fkey as the field is not the real value but the shown one
        if not self.field.fkey:
            self.master.field_widgets[self.field_name].field.widget.set_max_length()
                
        self.master.initialize_record_editing(path)
        self.master.commit_inhibited = False
        return True

    def remove_widget_cb(self, widget):
        """
        If the call has invalid data we don't want to remove the widget
        so that we can edit the wrong data rather then loosing what was already typed
        """
        if self.master.cell_entry and not self.master.cell_entry.is_valid():
            widget.stop_emission('remove-widget')
            return True
        self.master.cell_entry = None

    def focus_out_cb(self, widget, event, cell, path):
        if self.master.cell_entry:
            widget.activate()

class MultilineColumn(VarcharColumn):
    """
    A renderer able to show and edit in multiline mode. Very basic...
    """
    MIN_DEFAULT_WIDTH = 40

    
    def setup_cell_renderers(self, cell_renderer=None):

        width = self.get_width()

        cell = cell_renderers.MultilineCellRenderer(self.master)

        GenericColumn.setup_cell_renderers(self, cell_renderer=cell)
        cell.set_property('ellipsize', pango.ELLIPSIZE_END)
        cell.set_data('width', width)

        return cell

    def remove_widget_cb(self, widget):
        """
        If the call has invalid data we don't want to remove the widget
        so that we can edit the wrong data rather then loosing what was already typed
        """
        if self.master.cell_entry:
            self.master.cell_validate()

        self.master.cell_entry = None

    def focus_out_cb(self, widget, event, cell, path):

        if self.master.cell_entry:
            self.master.cell_validate()
            cell.emit("edited", cell.editor.get_data("path"), cell.editor.get_text())
            cell.editor.remove_widget()

    def editable_connects(self, editable):
        pass

class NumericColumn(VarcharColumn):
    """
    A renderer similar to varchar but with different expand options
    and with right justification
    """
    
    def get_width(self):
        
        if self.master.col_width and self.field_name in self.master.col_width:
            width = self.master.col_width.get(self.field_name, )
        else:
            if self.field.type == int:
                width = 8
            else:
                width = 10

        return width

    def set_alignment(self, cell):

        cell.set_property('xalign', 1.0)

    def editable_connects(self, editable):

        #VarcharColumn.on_activate(self, editable)
        editable.connect('key-press-event', self.master.digits_check_input_cb  )            

class FKeyColumn(VarcharColumn):
    """
    A renderer that shows the value instead of the id
    """
    MIN_DEFAULT_WIDTH = 15

    def cell_set_property(self, cell):

        VarcharColumn.cell_set_property(self, cell)
        cell.set_property('foreground', 'navyblue')
        
    def cell_data_func_cb(self, column, cell, model, iter, prop_name):
        """
        cell_data_function used by column that have fkey
        """

        if not column.get_visible():
            return

        obj = model.get_value(iter, 0)
        
        if not obj:
            return
        
        cell.set_property('visible', True)        

        ## DB RECORDS
        if isinstance(obj, self.master.mapper.class_):
            fkey_value = getattr(obj, self.field_name)

            if fkey_value is not None:
                path = model.get_path(iter)
                value = self.field.lookup_value(fkey_value)
                cell.set_property('text', value)
            else:
                cell.set_property('text', '')
            cell.set_property('editable', self.editable)

        ## TOTALS
        elif hasattr(self.master, 'totals') and isinstance(obj, self.master.totals.total_class):
            cell.set_property('text', '')
            cell.set_property('editable', False)        

        ## HEADER
        else:
            cell.set_property('text', getattr(obj, self.field_name))
            cell.set_property('editable', False)

    def editing_started_cb(self, cell, editable, path):
        
        VarcharColumn.editing_started_cb(self, cell, editable, path)
        model = self.column.get_tree_view().get_model()
        obj = model.get_value(model.get_iter(path), 0)
        ## I trust this value as it comes from the obj
        self.master.cell_entry.value = getattr(obj, self.field_name)

class DateColumn(VarcharColumn):

    """
    Will have bindings to change the date in a faster way
    possibly popping a calendar
    """

    MIN_DEFAULT_WIDTH = 10
    
    def editable_connects(self, editable):

        pass
        #editable.connect('key-press-event')
    
class DateTimeColumn(DateColumn):

    MIN_DEFAULT_WIDTH = 16
    
    def editable_connects(self, editable):

        pass
        #editable.connect('key-press-event')
    
class EnumColumn(VarcharColumn):

    RENDERER = gtk.CellRendererText
    RESIZE = True
    REORDER = True
    CLICK = True
    EXPAND = False
    MIN_DEFAULT_WIDTH = 4
    MAX_DEFAULT_WIDTH = 30
    PROPERTY = 'text'
    editable = False

    def cell_data_func_cb(self, column, cell, model, iter, prop_name):
        """
        cell_data_function used by column that have fkey
        """

        if not column.get_visible():
            return

        obj = model.get_value(iter, 0)
        
        if not obj:
            return
        
        cell.set_property('visible', True)        

        ## DB RECORDS
        if isinstance(obj, self.master.mapper.class_):
            value = getattr(obj, self.field_name)

            if value is not None:
                show_value = self.field.lookup_value(value)
                cell.set_property('text', show_value)
            else:
                cell.set_property('text', '')
            cell.set_property('editable', self.editable)

        ## TOTALS
        elif hasattr(self.master, 'totals') and isinstance(obj, self.master.totals.total_class):
            cell.set_property('text', '')
            cell.set_property('editable', False)        

        ## HEADER
        else:
            cell.set_property('text', getattr(obj, self.field_name))
            cell.set_property('editable', False)

class ImageColumn(GenericColumn):

    RENDERER = gtk.CellRendererPixbuf
    RESIZE = True
    REORDER = False
    CLICK = True
    EXPAND = False
    MIN_DEFAULT_WIDTH = 4
    MAX_DEFAULT_WIDTH = 30
    PROPERTY = 'pixbuf'
    editable = False

    def __init__(self, master, field_name, title, field=None):

        GenericColumn.__init__(self, master, field_name, title, field=None)
        try:
            master.treeview.props.has_tooltip = True
            master.treeview.connect('query-tooltip', self.return_image_path, )
        except AttributeError:
            pass

    def return_image_path(self, treeview, x, y, keyboard_mode, tooltip):
        "Set a tooltip with the file/image name"
        try:
            path, column, x_in_cell, y_in_cell = treeview.get_path_at_pos(x,y)
        except TypeError:
            return
        idx = path[0]
        if not idx: #header
            return
        path = tuple([idx-1])
        model = treeview.get_model()
        obj = model.get_value(model.get_iter(path), 0)
        file_path = getattr(obj, self.field_name)
        if file_path and (column.get_data('field_name') == self.field_name):
            tooltip.set_text(file_path)
            return True

    def set_editable(self, editable):
        pass
    def cell_set_property(self, cell):
        pass

    def setup_cell_renderers(self, cell_renderer=None):
        """
        setup cell renderers 
        """

        cell = cell_renderer or self.RENDERER()
        self.column.pack_start(cell, True)
        self.cell_set_property(cell)

        return cell
    
    def cell_data_func_cb(self, column, cell, model, iter, prop_name):
        """
        function set by set_cell_data_func
        gets the attribute from the field and render an image thumbnail
        """

        if not column.get_visible():
            return
        obj = model.get_value(iter, 0) 
        ## when the column is not representing a db-column (eg. is a python function)
        ## we pass the object itself to the function
        if self.field.persistent:
            value = getattr(obj, self.field_name)
        else:
            value = obj
            if isinstance(obj, self.master.mapper.class_):
                value = self.field.clean_value(value)

        cell.set_property('visible', True)        

        ## DB RECORDS
        if isinstance(obj, self.master.mapper.class_):
            cell.set_property('visible', True)
            if value:
                if not self.field.exists(value):
                    cell.set_property('pixbuf', None)
                    cell.set_property('stock-id', 'gtk-missing-image')
                    cell.set_data('thumbnail_path', None)
                    return

                if self.field.is_image(value):
                    thumbnail_path = value and self.field.get_thumbnail(value, complete_path=True) or None
                    if thumbnail_path:
                        if cell.get_data('thumbnail_path') != thumbnail_path:
                            pixbuf = gtk.gdk.pixbuf_new_from_file(thumbnail_path) if thumbnail_path else None

                            cell.set_property('pixbuf', pixbuf)
                            cell.set_property('stock-id', None)
                            cell.set_data('thumbnail_path', thumbnail_path)
                    else:
                        cell.set_property('pixbuf', None)
                        cell.set_property('stock-id', gtk.STOCK_MISSING_IMAGE)
                        cell.set_data('thumbnail_path', thumbnail_path)
                        
                else:
                    cell.set_property('pixbuf', None)
                    cell.set_property('stock-id', 'gtk-file')
                    cell.set_data('thumbnail_path', None)
            else:
                cell.set_property(prop_name, None)
                cell.set_data('thumbnail_path', None)
                cell.set_property('stock-id', None)
                

        ## TOTALS
        elif hasattr(self.master, 'totals') and isinstance(obj, self.master.totals.total_class):
            cell.set_property(prop_name, None)
            cell.set_data('thumbnail_path', None)
            cell.set_property('stock-id', None)

        ## HEADERS
        else:
            cell.set_property(prop_name, None)
            cell.set_data('thumbnail_path', None)
            cell.set_property('stock-id', None)
    
class CellEntry(object):
    """
    An object to store info on editable status
    Mainly needed to check if validation is required with FKey fields and m2m nested tables
    Completion sets valid to True, any manual edit invalidates, so that a field.validate() is
    triggered.
    Any movement (click of Tab or Down) away from a CellRenderer is inhibited if

      * a cell exists
      * the cell is not valid
      
    CellEntry is destroyed within 'remove-widget' signal callback of the editable

    FIXME: should probably be simplified being it only needed for FKey Columns/m2m
    """
    def __init__(self, editable, cell, path, field_name):

        self.entry = editable
        self.cell = cell
        self.path = path
        self.field_name = field_name
        self.valid = True
        self.text = editable.get_text()

        if isinstance(editable, gtk.Entry):
            # Multiline does not have 'canged' and does not need invalidating
            self.entry.connect('changed', self.on_editable_change)
        else:
            ## this is just a hack to force cell_validate() when browsing away
            self.valid = False
            
        self.substitute = False

    def on_editable_change(self, widget):
        self.valid = False

    def is_valid(self):
        
        valid = self.valid or self.text == self.entry.get_text()
        return valid

    def get_text(self):
        return self.entry.get_text()
    
    def __repr__(self):
        return "<CellEntry: (%s) %s>" % (self.valid, self.get_text())

class ColumnMenuProxy(object):
    def __init__(self, master, view):
        self.master = master
        self.view = view
        
#### column menu
    def popup_col_menu(self, ev, treeview, field_name):

        from sqlkit.layout.misc import StockMenuItem
        try:
            self.master.widgets['M=popup'].destroy()
        except:
            pass

        menu = self.master.widgets['M=popup'] = gtk.Menu()
        field = self.master.gui_fields[field_name]
        ## add to filter
        field_name_localized = self.master.get_label(field_name, gtk_label=True)
        if field.persistent:
            ## TIP: menu entry to add a filter in the filter panel
            label_str = _("Add a filter on '%s'") % field_name_localized
            item = StockMenuItem(label=label_str, stock='gtk-find')
    #        item.connect('activate', self.filter_panel.add, ev, field_name )
            item.connect('activate', self.master.filter_panel.add, ev, field_name, self.master )
            menu.append(item)

        ## sort
        item = gtk.ImageMenuItem('gtk-sort-ascending')
        item.connect('activate', self.reload_sort_cb, field_name, 'ASC' )
        if field.persistent:
            item.set_tooltip_text(_("Sort on this column reloading from the database, " + \
                                    "you can use 's' to sort locally"))
        else:
            item.set_tooltip_text(_("Sort on this column locally (w/o touching the database)"))
            
        menu.append(item)

        item = gtk.ImageMenuItem('gtk-sort-descending')
        item.connect('activate', self.reload_sort_cb, field_name, 'DESC' )
        menu.append(item)

        ## hide
        # TIP: column menu opt
        item = StockMenuItem(label=_("Hide this column"), stock='gtk-close')
        item.connect('activate', self.hide_fields_cb, field_name, self.view )
        menu.append(item)

        ## totals
        if field.type in (int, float, Decimal) and not isinstance(field, fields.ForeignKeyField):
            # TIP: column menu opt
            item = gtk.MenuItem(label=_("Create total"))
            item.connect('activate', self.add_total_cb, field_name )
            menu.append(item)

        menu.append(gtk.SeparatorMenuItem())
        ## subtotals
        if isinstance(field, fields.DateField):
            self.menu_add_date_total_break(menu, field_name)
        else:
            # TIP: column menu total
            item = gtk.MenuItem(label=_("Subtotal on %s") % (field_name_localized))
            item.connect('activate', self.add_subtotal_cb, field_name )
            menu.append(item)
        
        ## info
        # TIP: column menu opt
        item = gtk.ImageMenuItem('gtk-info')
        item.connect('activate', self.master.show_field_info, field_name )
        menu.append(item)

        menu.show_all()
        menu.popup(None, None, None, ev.button, ev.time)
        #menu.popup(None, None, None, 1, 1)

    def fill_menu_hide_fields(self):
        """
        Add menu for showing/hiding field columns
        """
        if not 'M=modify' in self.master.widgets:
            return
        menu = self.master.widgets['M=modify']
        # TIP: modify menu entry
        item_show = gtk.MenuItem(label=_("Show field"))
        item_hide = gtk.MenuItem(label=_("Hide field"))
        menu.append(item_show)
        menu.append(item_hide)
        
        self.menu_show = gtk.Menu()
        self.menu_hide = gtk.Menu()

        item_show.set_submenu(self.menu_show)
        item_hide.set_submenu(self.menu_hide)

        for field_name in self.master.field_list:
            field_name_localized = self.master.get_label(field_name, gtk_label=True)
            m = gtk.MenuItem(field_name_localized)
            m.connect('activate', self.hide_fields_cb, field_name)
            self.menu_hide.append(m)
            
        item_hide.set_submenu(self.menu_hide)
        menu.show_all()

    def hide_fields_cb(self, menuItem, field_name, view):
        view.hide_fields(field_name)
        
    def menu_add_date_total_break(self, menu, field_name):

        def add_break_date_cb(menu_item, field_name, period):
            self.master.totals.add_date_break(field_name, period)

        periods = [('day',_('day')), ('week',_('week')), ('month',_('month')),
                   ('quarter',_('quarter')), ('year',_('year'))]

        for period, trad in periods:
            item = gtk.MenuItem(label=_("Subtotals by %s") % trad)
            item.connect('activate', add_break_date_cb, field_name, period)
            menu.append(item)
        
    def add_total_cb(self, menu_item, field_name):

        try:
            self.master.totals.add_total(field_name, quiet=True)
        except AttributeError:
            # mmh this is from filter panel!
            from . import totals
            self.master.totals = totals.Totals(self.master,
                                               treeview=self.master.filter_panel.view.treeview)
            self.master.totals.add_total(field_name)
            
        
    def add_subtotal_cb(self, menu_item, field_name):
        self.master.totals.add_break(field_name)

    def menu_add_toggle_column(self, field_name, view):
        """
        Add a menu entry to show columns in the menu 'modify' or change it's
        visibility according to real state of the column. A column can be toggled back
        using the view menu (left click on the TreeView)
        """

        action_name = 'field_%s' % field_name
        action = view.ui_manager.get_action('/TreePopup/Columns/ShowColumns/%s' % action_name)
        if not action:
            view.actiongroup_view.add_actions([
                (action_name, None, self.master.get_label(field_name, gtk_label=True),
                 None, None, view.show_column,),
                ], field_name)

            menu_def = '''
              <popup name="TreePopup">
                 <placeholder action="Columns" >
                    <menu action="ShowColumns" >
                         <menuitem action="%s" />
                    </menu>
                 </placeholder>
               </popup>
            ''' % action_name

            view.ui_manager.add_ui_from_string(menu_def)
        else:
            action.set_visible(not action.get_visible())
            
        view.hide_column(field_name)
        
    def reload_sort_cb(self, widget, field_name, direction):

        from sqlkit.db.utils import tables, get_description

        if self.master.relationship_leader or field_name not in self.master.mapper_info:
            ## related table are ordered locally via modelproxy.order_by
            if direction == "DESC":
                field_name = "-" + field_name
            self.master.modelproxy.order_by(field_name)
        else:
            ## main tables are ordered in the db, a local order can be obtained
            ## via 's' (sort) key press
            self.master.modelproxy.order_by(None)
            order_by = field_name
            if self.master.is_fkey(field_name):
                ftable = getattr(self.master.mapper.c, field_name
                                 ).foreign_keys.copy().pop().column.table
                fdescr = get_description(ftable, attr='description')
                order_by = "%s__%s" % (field_name, fdescr)


            if direction == 'DESC':
                order_by += ' DESC'

            self.master.order_by = order_by
            self.master.reload_cb(None)
        
    
class View(object):

    """

    A View is a set of columns of the SqlTable's that offers a (possibly
    partial) view of the model. Each SqlTable has one mandatory view named
    ``main`` and possibly other views. Attribute :attr:`sqlkit.widgets.SqlTable.views` (a
    sqlkit.utils.Container) stores them.

    It can be used to provide different way to look at the same data
    (e.g. different cell-renderers) or different columns for long ones

    """
    def __init__(self, master, name, treeview=None, field_list=None, cell_renderers=None, ro=False):
        """
        :param master: the SqlTable this view belongs to
        :param treeview: the treeview where the columns live
        :param cell_renderers: a dict of cell_renderers for each column
        :param ro: make it read-only (default: False)
        """
#        assert field_list is not None, "Field_list cannot be None"
        assert treeview is not None, "You need to set the Treeview"
        self.master = master
        self.name = name
        self.treeview = treeview
        self.read_only = ro
        treeview.set_data('view', self)

        self.field_list = str2list(field_list)
        self.tvcolumns = {}
        self.columns = {}
        self.cell_renderers = {}

        if self.field_list:
            self.master.setup_field_validation(self.field_list)
        self.setup_columns()
        if not name in ('main',):
            ## for 'main' I do that later so that master.actiongroup_* will be ready
            self.create_column_menu()

        if hasattr(self.master, 'cursor_changed_cb'):
            self.treeview.connect('cursor-changed', self.master.cursor_changed_cb, self)
            self.treeview.connect('key-press-event', self.master.keypress_event_cb, self)
            self.treeview.connect('button-press-event', self.master.button_press_event_cb, self)

        self.treeview.set_enable_search(False)
        self.treeview.show_all()
        
        self.treeview.set_rules_hint(True)
        # set selection mode
        treeselection = self.treeview.get_selection()
        treeselection.set_mode(gtk.SELECTION_SINGLE)
        # callback for selection changes
        if name == 'main':
            treeselection.connect('changed', self.master.selection_changed_cb)
        ## sync the different selections
        treeselection.connect('changed', self.selection_changed_cb, self)
        treeview.connect('row-collapsed', self.row_collapsed_cb, self)
        treeview.connect('row-expanded', self.row_expanded_cb, self)
        treeview.connect('key-press-event', self.keypress_event_cb)

    def keypress_event_cb(self, wdg, event, view=None):

        pre = 'tree'
        ksym = gtk.gdk.keyval_name(event.keyval)
        mods = ['key_' + pre]
        ## mod2 gets in the way when you press the NumLock: I don't want
        ## to depend on that, as I'm not usng it!!!
        for prefix, mask in [('ctrl', gtk.gdk.CONTROL_MASK),
                             ('shift', gtk.gdk.SHIFT_MASK),
                             ('alt', gtk.gdk.MOD1_MASK),
                             #('mod2', gtk.gdk.MOD2_MASK),
                             ('mod3', gtk.gdk.MOD3_MASK),
                             ('mod4', gtk.gdk.MOD4_MASK),
                             ('mod5', gtk.gdk.MOD5_MASK),]:
            if event.state & mask:
                mods.append(prefix)

        ksym = '_'.join(mods + [ksym])
        if ksym in dir(self):
            return getattr(self, ksym)(wdg, event)

    def key_tree_b(self, treeview, event):
        "brake: sort the treeview on this column and add a subtotal for this field"

        field_name = self.get_field_name_from_pointer(treeview)
        if self.master.modelproxy._order_list == [(field_name, True)]:
            field_name = "-" + field_name
        self.master.modelproxy.order_by(field_name)
        self.master.totals.add_break(field_name)
        
    def key_tree_shift_B(self, treeview, event):
        "brake: get rid of subtotals"
        
        field_name = self.get_field_name_from_pointer(treeview)
        if self.master.modelproxy._order_list == [(field_name, True)]:
            field_name = "-" + field_name
        self.master.modelproxy.order_by(field_name)
        self.master.totals.break_func = None
        self.master.totals.compute()
        
    def key_tree_f(self, treeview, event):
        "filter: add a filter for this column"
        field_name = self.get_field_name_from_pointer(treeview)
        if field_name and field_name in self.master.mapper_info:
            self.master.filter_panel.add(None, None, field_name, self.master)
        
    def key_tree_h(self, treeview, event):
        "hide: hide this column"
        field_name = self.get_field_name_from_pointer(treeview)
        self.hide_fields(field_name)

    def key_tree_s(self, treeview, event):
        "sort: sort the treeview on this column"
        field_name = self.get_field_name_from_pointer(treeview)

        if self.master.modelproxy.get_order() == (field_name, True):
            field_name = "-" + field_name
        self.master.modelproxy.order_by(field_name)
        
    def key_tree_t(self, treeview, event):
        "totals: add total to the column"

        field_name = self.get_field_name_from_pointer(treeview)
        self.menu.add_total_cb(None, field_name)
        
    def key_tree_v(self, treeview, event):
        """toggle row visibility if a function has been set via
        :meth:`sqlkit.common.SqlTable.add_row_filter` """

        self.master.modelproxy._filter_rows = not self.master.modelproxy._filter_rows
        self.master.record_refresh()
        
    def key_tree_shift_Z(self, treeview, event):
        """zoom-fit
        I would have preferred Control-z but it's kidnapped by global action shortcut
        """
        self.on_zoom_fit(self)
        
    def get_field_name_from_pointer(self, treeview=None):

        x, y, modifier_state = self.treeview.window.get_pointer()
        try:
            path, column, x_in_cell, y_in_cell = self.treeview.get_path_at_pos(x,y)
            #iter = self.master.modelproxy.modelstore.get_iter(path)
            field_name = column.get_data('field_name')
            return field_name
        except TypeError, e:
            return

    def selection_changed_cb(self, treeview, view):
        """
        used to keep selections in sync
        """
        for view in self.master.views:
            if view != self:
                view.select_path(self.get_selected_path())

    def row_expanded_cb(self, treeview, iter, path, view):
        """
        used to keep selections in sync
        """
        for view in self.master.views:
            if view != self:
                view.treeview.expand_row(path, True)

    def row_collapsed_cb(self, treeview, iter, path, view):
        """
        used to keep selections in sync
        """
        for view in self.master.views:
            if view != self:
                view.treeview.collapse_row(path)

    def set_field_list(self, field_list, ):
        """
        Set field of visible columns. Accepts both a list or a string (space or comma separated)

        :param field_list: the field name list
        :param view: the view for which we set the field_list
        """
        from copy import copy

        field_list = str2list(field_list)
        orig_field_list = copy(self.field_list)
        for field_name in field_list:
            if field_name in self.master.mapper_info.fields:
                ## is already known, just make it visible
                self.tvcolumns[field_name].set_property('visible', True)
            else:
                raise NotImplementedError("Column %s is not kown in self.mapper_info.fields" % field_name)
        for field_name in orig_field_list:
            if field_name not in field_list:
                self.tvcolumns[field_name].set_property('visible', False)
            
        prev = None
        for field_name in field_list:
            self.treeview.move_column_after(self.tvcolumns[field_name], prev)
            prev = self.tvcolumns[field_name]
            
        self.field_list = field_list
        

    def hide_fields(self, field_name_list):
        """
        Hide a column and add the entry in the menu to make it show up again

        :param field_name_list: may be a list or a string (in which case it is split with, and spaces)
        :param view: the view for which we set the list of hidden fields

        """

        field_name_list = str2list(field_name_list)
        
        if len(field_name_list) == 0:
            field_name_list = self.hidden_fields

        self.hidden_fields = field_name_list

        if not self.tvcolumns:
            return

        for field_name in field_name_list:
            self.menu.menu_add_toggle_column(field_name, self)


    def on_zoom_fit(self, widget=None, *args):

        tv_utils.zoom_to_fit(self.treeview, resize=True)

    def fix_expandable_columns(self):
        """
        If no column is expandable, make all columns expandable:
        it's very ugly to see just the last one expand
        """

        fix_it = True
        for key, col in self.tvcolumns.iteritems():
            if col.get_property('expand'):
                fix_it = False

        if fix_it:
            for key, col in self.tvcolumns.iteritems():
                col.set_property('expand', True)
            
    def hide_column(self, field_name):

        self.tvcolumns[field_name].set_property('visible', False)
        self.master.sb(_("Right click on this table to show the column again"), seconds=10)
        
    def show_column(self, item, field_name):
        
        self.menu.menu_add_toggle_column(field_name, self)
        self.tvcolumns[field_name].set_property('visible', True)
        
    def create_column_menu(self):

        from sqlkit.widgets.common import uidescription

        self.ui_manager = gtk.UIManager()
        self.ui_manager.connect('connect-proxy', self.master.uimanager_connect_proxy)
        self.accel_group = self.ui_manager.get_accel_group()
        if self.master.is_toplevel():
            self.master.widgets['Window'].add_accel_group(self.accel_group)


        self.actiongroup_view = gtk.ActionGroup('View')
        self.actiongroup_view.add_actions([
            ('ExportView', None, _('Export'), None, _('Export these data into csv format'),
             self.master.export),
            ], self.name)
        self.actiongroup_view.add_actions([
            ('Zoom-fit', gtk.STOCK_ZOOM_FIT, None, '<Control>z',
             _('Adapt width of columns to data'), self.on_zoom_fit),
            ('ShowColumns', None, _('Show field')),  # menuitem
            ('HideColumns', None, _('Hide field')),  # menuitem
            ])

        try:
            self.ui_manager.insert_action_group(self.master.actiongroup_table, 10)
            self.ui_manager.insert_action_group(self.master.actiongroup_insert, 12)
            self.ui_manager.insert_action_group(self.master.actiongroup_delete, 13)
            self.ui_manager.add_ui_from_string(uidescription.TREEPOPUP)
        except AttributeError:
            pass

        self.ui_manager.insert_action_group(self.actiongroup_view, 14)

        self.ui_manager.add_ui_from_string(COLUMN_MENU)
        self.menu = ColumnMenuProxy(self.master, self)


    def pop_menu(self, treeview, event, obj, field_name):

        ## enable/disable menu entries
        action = self.ui_manager.get_action('/TreePopup/MaskView')
        action.set_sensitive(obj and True or False)
            
        action_fk = self.ui_manager.get_action('/TreePopup/MaskViewFKey')
        if field_name and self.master.gui_fields[field_name].fkey:
            action_fk.set_visible(True)
            label = self.master.get_label(field_name, gtk_label=True)
            action_fk.set_property('label', _("View '%s' in a Mask") % label)
        else:
            action_fk.set_visible(False)
            
        action_upload_image = self.ui_manager.get_action('/TreePopup/UploadImage')
        if obj and field_name and self.master.is_image(field_name):
            action_upload_image.set_visible(True)

            # don't show missing images...
            action_show_image = self.ui_manager.get_action('/TreePopup/ShowFile')
            filename = getattr(obj, field_name)
            if obj and filename and self.master.gui_fields[field_name].exists(filename):
                action_show_image.set_sensitive(True)
            else:
                action_show_image.set_sensitive(False)

        else:
            action_upload_image.set_visible(False)
            
        action_new_child = self.ui_manager.get_action('/TreePopup/NewChild')
        if self.master.modelproxy.is_tree():
            new = self.ui_manager.get_action('/TreePopup/New').get_visible()
            action_new_child.set_visible(new)
        else:
            action_new_child.set_visible(False)
            

        action_delete_file = self.ui_manager.get_action('/TreePopup/DeleteFile')
        action_show_file = self.ui_manager.get_action('/TreePopup/ShowFile')
        action_save_file = self.ui_manager.get_action('/TreePopup/SaveFile')
        if obj and field_name and (self.master.is_image(field_name) or
                               self.master.is_file(field_name)) and \
                               getattr(obj, field_name):
            action_delete_file.set_visible(True)
            action_show_file.set_visible(True)
            action_save_file.set_visible(True)
        else:
            action_delete_file.set_visible(False)
            action_show_file.set_visible(False)
            action_save_file.set_visible(False)
            
        action_upload_file = self.ui_manager.get_action('/TreePopup/UploadFile')
        if field_name and self.master.is_file(field_name):
            action_upload_file.set_visible(True)
        else:
            action_upload_file.set_visible(False)
            
        action_delete = self.ui_manager.get_action('/TreePopup/RecordDelete')
        action_delete.set_sensitive(obj and True or False)

        menu = None
        if event.button == 3:
            self._field_name = field_name
            menu = self.ui_manager.get_widget('/TreePopup')
            menu.popup(None, None, None, event.button, event.time)
        
        return menu

    def setup_columns(self, field_list=None, position=-1):
        """
        :param field_list: list of field_names or string to be splitted (comma or space separated)
        :param position: determine the position in the columns where the column will be inserted
        """

        for field_name in field_list or self.field_list:
            
            if field_name in widgets.info:
                label = widgets.info[field_name][0]
            else:
                label = field_name

            ## first check if you have a Custom Renderer
            if self.cell_renderers and field_name in self.cell_renderers:
                col = self.cell_renderers.get(field_name)(field_name, label)

            elif self.master.is_fkey(field_name) :   ## FKey
                col = FKeyColumn(self.master, field_name, label)

            elif self.master.is_image(field_name):  ## image
                col = ImageColumn(self.master, field_name, label)

            elif self.master.is_enum(field_name):  ## image
                col = EnumColumn(self.master, field_name, label)

            elif self.master.is_boolean(field_name):  ## boolean
                col = BooleanColumn(self.master, field_name, label)

            elif self.master.is_date(field_name):   ## Dates
                col = DateColumn(self.master, field_name, label)

            elif self.master.is_datetime(field_name):  ## Datetime
                col = DateTimeColumn(self.master, field_name, label)

            elif self.master.is_number(field_name):  ## Number
                col = NumericColumn(self.master, field_name, label)

            elif self.master.is_text(field_name):  ## Multiline
                col = MultilineColumn(self.master, field_name, label)

            elif self.master.is_string(field_name):  ## Varchar
                col = VarcharColumn(self.master, field_name, label)

            else:
                col = VarcharColumn(self.master, field_name, label)

            self.add_column(col, position=position)
            
        self.treeview.columns_autosize()
        self.fix_expandable_columns()
            
    def add_column(self, column=None, position=-1, field=None):
        """
        Add a column to the view. 

        :param column: the column to be added. If empty, a field must be provided 
        :param position: where should the column be inserted
        :param field: an instance of the Field that should be used. In this case a
              column is guessed and built on the fly by :meth:`setup_columns`
        """
        if not column:
            assert field is not None, \
                   "You must pass a sqlkit.fields.Field instance"
            self.master.gui_fields[field.field_name] = field
            self.setup_columns([field.field_name], position=position)
            return

        self.tvcolumns[column.field_name] = column.column
        self.columns[column.field_name] = column
        if position  < 0:
            self.treeview.append_column(column.column)
        else:
            self.treeview.insert_column(column.column, position)
        if self.read_only:
            column.set_editable(False)
        
    def get_first_editable_col(self):
        """
        return the first visible col to position the cursor on
        """
        
        columns = self.treeview.get_columns()
        second_choice = []
        for field_name in [c.get_data('field_name') for c in self.treeview.get_columns()]:
            if self.tvcolumns[field_name].get_visible() and self.master.is_editable(field_name):
                try:
                    has_usable_default = self.master.gui_fields[field_name].get_default()
                except exc.NotHandledDefault, e:
                    # it's not necessary to fill this value as a default exists even if we're
                    # not able to handle it
                    has_usable_default = True
                if has_usable_default is not None:
                    second_choice += [self.tvcolumns[field_name]]
                else:
                    return self.tvcolumns[field_name]
        if second_choice:
            return second_choice[0]

    def start_editing(self, path, field_name=None):
        """
        Edit a path/column. Column is passed by its field_name

        :param path: the path to be edited
        :param field_name: the field_name of the column, if None, the first editable field
            that does not have a default
        """

        if field_name:
            col = self.tvcolumns[field_name]
        else:
            col = self.get_first_editable_col()
        self.treeview.scroll_to_cell(path, col)
        self.treeview.set_cursor(path = path, focus_column = col,  start_editing = True)
        
    def get_selected_path(self):
        """Return the path of the selected row or None

        NOTE: treeselection 'changed' signal arrives when the selection changed has
              alreadu occurred

        """
        selection = self.treeview.get_selection()
        model, rows = selection.get_selected_rows()
        ## we use just the first selected
        #  >>> sel.get_selected_rows()
        #  (<gtk.Modelproxy.Modelstore object at 0x8dd61bc (GtkModelproxy.Modelstore at 0x8da6090)>, [(1,)])

        if rows:
            return rows[0]
        else:
            return None
    
    def __str__(self):
        return "<View: %s>" % self.name

    
    def select_path(self, path=None, obj=None, sync=True):
        """
        Select path ``path``. If path is null and obj is not null try finding path at which is obj


        :param path:  the path to be selected or None
        :param obj:  if path is None, the object to be searched for and selected
        :param sync: syncronize all views but run just one selection_cb
        :type sync: boolean
        """
        def search_obj(model, path, iter, (obj, path_list)):
            if model.get_value(iter, 0) == obj:
                path_list += [path]
                return True

        ## let's find out the real path for the object. The object may be in a
        ## TreeStore's deeper level or some totals may shift it 

        if path is None and obj:
            path_list = []
            self.master.modelproxy.modelstore.foreach(search_obj, (obj, path_list))
            try:
                path = path_list[0]
            except IndexError:
                pass

        if path is not None:
            self.treeview.get_selection().select_path(path)
