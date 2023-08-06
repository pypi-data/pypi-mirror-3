# Copyright (C) 2005-2010, Sandro Dentella <sandro@e-den.it>
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
SqlTable: a widget to edit sql in table mode

a model (self.listore) holds one single instance of the class is linked with the
mapper. column.set_cell_data_func on each column will set the value from there.

"""


import sys
import re
import os
import gtk
import weakref
import shutil
import datetime

import gobject
import gtk
import sqlalchemy

import sqlkit
from sqlkit import debug as dbg, _, exc, fields
from sqlkit.layout import widgets, get_label
from sqlkit.misc.utils import Container, str2list, open_file
import utils as tv_utils
import cell_renderers
import totals
from sqlkit.widgets.common import sqlwidget, dialogs
from modelproxy import ModelProxy
from sqlkit.widgets.table.columns import View
from sqlkit.widgets.table.tablewidgets import CellWidget

class SqlTable(sqlwidget.SqlWidget):
    """
    Main widget to represent data of a sqlalchemy selectable (SELECT of a TABLE or JOIN
    & similar).

    A SqlTable can have different :ref:`views <views>` of the same data
    represented in different TreeViews.

    A SqlTable can be viewed alone or as part of a composite widget, that is
    normally a mask with :ref:`relationships`: be sure to understand this
    part as it's probably one of the more powerfull features of Sqlkit.

    SqlTables can have both ListStores or TreeStores. The latter allows to represent
    rows in a hierarchy.

    SqlTable inherits from :class:`sqlkit.widgets.common.sqlwidget.SqlWidget`

    """
#### Signals
    __gsignals__ = {
        'button-press-event' : (gobject.SIGNAL_RUN_LAST,
                           gobject.TYPE_BOOLEAN,
                                # event, obj, field_name, treeview, view
                           (gobject.TYPE_PYOBJECT, gobject.TYPE_PYOBJECT, gobject.TYPE_STRING,
                            gobject.TYPE_PYOBJECT, gobject.TYPE_PYOBJECT),
                           ),
        'context-changed' : (gobject.SIGNAL_RUN_LAST,
                           gobject.TYPE_BOOLEAN,
                                # current (or None)
                           (gobject.TYPE_PYOBJECT,),
                           ),
        }

    views = None
    "A container for the possible :ref:`views`. It always have a default view named ``main``"

    totals = None
    "class for :ref:`totals`: see the specific documentation for further info"
    
    edited_path = None
    ## For some reason :meth: is not turned in a link...
    """The path of the edited row (a tuple). It's not the output of
    :meth:`get_selected_path` since when you change the selected row the
    validation is triggered on the *previuos* selected_row that is pointed
    to by ``edited_path``. 
    """

#    __metaclass__ = dbg.LogTheMethods
    currently_edited_field_name = None
    mapper = None
    cell_entry = None
    cell_renderers = None
#    commit_allowed = dbg.TraceIt(True, name='commit_allowed', mode='rw')
#### Init & Layout         
    def __init__(self, *args, **kwargs):

        self.views = Container()
        #self.views['main'] = View(self, 'main', )
        #self.treeview = None
        self.commit_inhibited = False
        self.deleting_row = False
        #self.edited_row_model_path = dbg.TraceIt(True, name='edited_row_model_path', mode='rw')
        self.edited_row_model_path = None
        self.modelproxy = ModelProxy(self, treeview=None)
        sqlwidget.SqlWidget.__init__(self, *args, **kwargs)
        self.modelproxy.treeview = self.treeview
        self.modelproxy.update()
        self.totals = totals.Totals(self)
        self._fk_layout_nick = {}
        self.run_hook('on_init')
        self._new_record = None
        
    def _get_layout(self, lay, naked):

        sqlwidget.SqlWidget._get_layout(self, lay, naked)
        self.treeview = self.widgets["TV=tree"]
        self.widgets['S=tree'].set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        ## from now on, the real field_list is the one in the View
        self.views['main'] = self.create_view(name='main', field_list = self.field_list, treeview=self.treeview)
        ## let tree use all the available space... 
        if not self.naked:
            self.lay_obj.prop('A.external','yscale',1)

        if self.rows:
            gobject.idle_add(self.set_rows)

        self.icon_setup()
        self.treeview.hide()
        self.treeview.show()
        gobject.idle_add(tv_utils.set_optimal_width, self.treeview)
        return (self.lay_obj, self.widgets)

    def icon_setup(self):
        """
        setup icons at the botton of the table if any 'icons' was passed to sqlwidget
        """
        if 'A.icons' not in self.widgets:
            return
        
        self.lay_obj.prop(
            ('A.icons', 'xscale', 0),
            ('A.icons', 'xalign', 0),
            ('A.icons', 'top-padding', 0),
            ('A.icons', 'bottom-padding', 0),
            ('A.icons', 'left-padding', 0)
            )
        ## just icons, no text
        if self.icons:
            for b in self.icons.split(" "):
                self.widgets[b].set_label = None
                self.widgets[b].get_image().set_property('icon-size', 1)
                ## in windows I can't see it...
                self.widgets[b].get_image().show()
                alignment = self.widgets[b].get_children()[0]
                hbox = alignment.get_children()[0]
                image, label = hbox.get_children()
                label.set_text('')

        
    def setup_field_validation(self, field_list=None):
        """
        Create sqlkit.fields.Field object: one for each handled field
        """
        if not field_list:
            return

        field_chooser = fields.FieldChooser(self.mapper_info,
                                            gui_field_mapping=getattr(self, 'gui_field_mapping', None))
        for field_name in field_list or self.field_list:
            if field_name not in self.gui_fields:
                db_spec = self.mapper_info.fields.get(field_name, None)
                Field = field_chooser.get_field(field_name, db_spec)
                field = Field(field_name, db_spec)
                self.gui_fields[field_name] = field

                field.set_master(self)
                field.set_widget(widget=CellWidget)

                self.field_widgets[field_name] = field.widget

    def create_view(self, name='main', treeview=None, field_list=None):
        """
        Create a :ref:`view <views>`, i.e.: a list of columns one for each
        field in self.field_list. Columns are setup according to the type of
        the database field, introspected from the mapper. There may be more
        than one view in a SqlTable. The first one is created mandatorily;
        possible further ones are created by hand, passing a view name, a
        treeview and -normally- a field_list. The filter panel output page
        is a view of the filtered records.

        All the views of a SqlTable share the same model.
        
        :param view: the name of the view
        :param treeview: the treeview
        :param field_list: a list of field_name for which we want the view
        """

        view = View(master=self, name=name, treeview=treeview, field_list=field_list)
        view.treeview.set_model(self.modelproxy.modelstore)
        self.set_rows(view=view)
        self.views[name] = view
        return view

    def show(self, show):
        sqlwidget.SqlWidget.show(self, show)
        self.views['main'].create_column_menu()
        self.views['main'].menu.fill_menu_hide_fields()
        
    def set_rows(self, rows=None, view=None, view_name=None):
        """
        set number of treeview visible rows to "rows"

        :param rows: number of rows (defaults to self.rows)
        :param view: the view. Defaults to None (all views)
        :param view_name: the name of the view. Defaults to None (all views)
        """
        if rows:
            self.rows = rows
        views = self.views
        if view:
            views = (view,)
        if view_name:
            views = (self.views[view_name])
        if not view:
            for v in views:
                tv_utils.set_height_request(v.treeview, self.rows)

    def hide_fields(self, field_name_list='', view_name='main'):
        """
        Hide a column and add the entry in the menu to make it show up again

        :param field_name_list: may be a list or a string (in which case it is split with, and spaces)
        :param view: the view for which we set the list of hidden fields

        """
        assert view_name in self.views, "Missing view_name: %s" % view_name
        self.views[view_name].hide_fields(field_name_list)
        
    def set_field_list(self, field_list, view_name='main'):
        """
        Set field of visible columns. Accepts both a list or a string (space or comma separated)

        :param field_list: the field name list
        :param view: the view for which we set the field_list
        """
        assert view_name in self.views, "Missing view_name: %s" % view_name
        self.views[view_name].set_field_list(field_list)

    def _get_edited_path(self):
        "return the curretly edited path as a tuple"

        try:
            return self.edited_row_model_path and \
                   tuple(int(x) for x in self.edited_row_model_path.split(':'))
        except AttributeError:
            ## edited_row_model_path may also be already a tuple...
            if isinstance(self.edited_row_model_path, tuple):
                return self.edited_row_model_path
                   
            

    edited_path = property(_get_edited_path)

###### Actions/UiManager
    def prepare_actions(self):
        """
        Prepare action needed by UIManager
        """
        sqlwidget.SqlWidget.prepare_actions(self)

        self.actiongroup_table   = gtk.ActionGroup('Table')

        self.actiongroup_insert.add_actions([
            ('Duplicate', gtk.STOCK_SAVE_AS, _('Duplicate'), None,
             _('Create a new row as a duplicate of this one'), self.record_save_new_cb),
            ('New', gtk.STOCK_NEW,   None, '', None, self.record_new_cb),
            ('NewChild', gtk.STOCK_NEW,   _('New child row'), '',
             _("Create e new row as child of this one"), self.record_new_child_cb),
            ])
        self.actiongroup_delete.add_actions([
            ('Delete', gtk.STOCK_DELETE, None, '<Control>k', None, self.record_delete),
            ('RecordDelete', gtk.STOCK_DELETE, None, None, None, self.record_delete3),
            ])

        self.actiongroup_table.add_actions([
            ('Zoom-fit', gtk.STOCK_ZOOM_FIT, None, '<Control>z', None, self.on_zoom_fit),
            ('ShowColumns', None, _('Show field')),  # menuitem
            ('HideColumns', None, _('Hide field')),  # menuitem
#            ('VisibleColumns', None, None),          # menu
#            ('HiddenColumns', None, None),           # menu
            ('Records', None, 'Records'),
            ('MaskView', gtk.STOCK_ZOOM_IN, _('View this record in a Mask'), '<Control>m', None, self.record_in_mask),
            ('MaskViewFKey', gtk.STOCK_LEAVE_FULLSCREEN, _('View this ForeignKey in a Mask'), None, None, self.fkey_record_in_mask),
            ('UploadImage', None, _('Upload Image'), None, None, self.upload_image),
            ('UploadFile', None, _('Upload File'), None, None, self.upload_file),
            ('DeleteFile', None, _('Delete File/Image'), None, None, self.delete_file),
            ('ShowFile', None, _('Show File/Image'), None, None, self.show_file),
            ('SaveFile', None, _('Save File/Image'), None, _('Save file locally'), self.save_file),
            ])
        self.actiongroup_table.add_actions([
            ('Export', None, _('Export'), None, None, self.export),
            ], 'main')
    def prepare_uimanager(self):

        from sqlkit.widgets.common import uidescription
        
        sqlwidget.SqlWidget.prepare_uimanager(self)
        self.ui_manager.insert_action_group(self.actiongroup_table, 1)

        self.ui_manager.add_ui_from_string(uidescription.TABLE_UI)

        self.ui_manager.get_action('/Main/Go/Forward').set_visible(False)
        self.ui_manager.get_action('/Main/Go/Back').set_visible(False)

    def set_mode(self, mode=None, reset=False, delay=False):

        sqlwidget.SqlWidget.set_mode(self, mode, reset=reset, delay=delay)

        if not delay and hasattr(self, 'columns'):
            for field_name, col in self.columns.iteritems():
                if field_name not in self.noup:
                    col.set_editable(True and 'u' in self.mode)
                else:
                    col.set_editable(False)
    mode = property(sqlwidget.SqlWidget.get_mode, set_mode)
        
#### callbacks treeview
    def selection_changed_cb(self, treeselection):
        """
        Main callback triggered when the TreeSelection changes. When run
        this function tries to record_save()
        """
        try:
            del self._clicked_obj
        except AttributeError:
            pass
        
        # selection changes in several different ways:

        # 1. no selection -> selection of existing row
        # 2. no selection -> selection on new row
        # 3. no selection -> reload (does it change?)
        # 4. selected existent record -> reload
        # 5. selected existent record -> other record
        # 6. selected existent record -> new record
        # 7. selected existent record -> delete
        # 8. selected existent LAST record -> delete

        if self.edited_row_model_path is None:
            self.emit('record-selected')
            obj = self.get_selected_obj()
            if not isinstance(obj, self.mapper.class_):
                # we have visited a total or something else
                return
            
            if obj or len(self.records):
                self.emit('context-changed', obj or self.records[0])
        ## commit_allowed is a flag that prevents .commit() if a new object
        ## has been created but not yet filled: it wouldn't validate
        if not self.commit_inhibited:
            try:
                if self.relationship_mode == 'm2m' and not self.m2m_editable:
                    ## a new record means a record that has not been substituted by completion
                    ## after completion-match the record is in the session but not in session.new
                    self.record_save(discard_unchanged=False, discard_new=True)
                else:
                    self.record_save(discard_unchanged=True)
                self.edited_row_model_path = None
            except exc.ValidationError, e:
                path = self.edited_row_model_path
                self.edited_row_model_path = None
                self.treeview.get_selection().select_path(path)
                self.edited_row_model_path = path                
                return True

        self.emit('record-selected')
        if self.get_selected_obj() or len(self.records):
            self.emit('context-changed', self.get_selected_obj() or self.records[0])
        return False
    
    def select_cursor_row_cb(self, treeview, start_editing, user_data):
        return False
    
    def cursor_changed_cb(self, treeview, view):
        return False
        
    def show_column(self, menuItem, field_name, view_name='main'):

        view = self.views[view_name]
        view.show_column(field_name)

    def button_press_event_cb(self, treeview, event, view):
        """
        Block browsing if last edited cell didn't validate
        """
        if self.cell_entry and not self.cell_entry.is_valid():
            if not self.cell_validate():
                return True
            
        ## emit button-press-event of the sqlwidget: event, field_name, value
        #  this happens before the selection gets changed so we cannot use get_selected_obj()

        try:
            path, column, x_in_cell, y_in_cell = treeview.get_path_at_pos(int(event.x),int(event.y))
            iter = self.modelproxy.modelstore.get_iter(path)
            obj = self.modelproxy.modelstore.get_value(iter,0)
            if isinstance(obj, self.totals.total_class):
                obj = None
            field_name = column.get_data('field_name')
            self._enforce_first_click_just_selects(path, column, field_name)
        except TypeError, e:
            obj = None
            field_name = None
            path = None

        self._clicked_obj = obj  # should I officially document it?
        self._clicked_path = path  # should I officially document it?
        self._field_name = field_name  # should I officially document it?
            
        menu = view.pop_menu(treeview, event, obj, field_name)
        self.emit('button-press-event', event, obj, field_name, menu, treeview)
        
        if event.button == 3:
            return True
        return False

    def _enforce_first_click_just_selects(self, path, column, field_name):
        """
        if selection has changed with a click on a toggle cell, turn that
        cell into insensitive to prevent changeing the value
        """
        
        ## I want the first click on the table to just change the selection, not the value
        ## the problem is that toggled signal happens *before* change in selection, so that
        ## all normal checks based on selection_changed are not yet at work
        selection = self.treeview.get_selection()
        model, rows = selection.get_selected_rows()
        if rows:
            selected_path = rows[0]
        else:
            selected_path = None

        if not path == selected_path and self.gui_fields[field_name].type == bool:
            if column.get_data('cell').get_property('mode') == gtk.CELL_RENDERER_MODE_ACTIVATABLE:
                column.get_data('cell').set_property('mode', gtk.CELL_RENDERER_MODE_INERT)
                gobject.idle_add(column.get_data('cell').set_property, 'mode', gtk.CELL_RENDERER_MODE_ACTIVATABLE)
        
    def on_zoom_fit(self, widget, *args):

        tv_utils.zoom_to_fit(self.treeview, resize=True)

#### event handling 
    def keyrelease_event_cb(self, wdg, event, data=None):
        return self.length_control(wdg, data)
    
    def keypress_event_cb(self, wdg, event, view=None):

        if isinstance(wdg, gtk.TreeView):
            pre = 'tree'
        else:
            #self.length_control(wdg, data)
            pre = 'entry'
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

    def key_tree_shift_ISO_Left_Tab(self, treeview, event, data):

        path, col = self.treeview.get_cursor()
        columns = self.treeview.get_columns()
        colnum = columns.index(col)
        if colnum - 1 >= 0:
            gobject.idle_add(self.treeview.set_cursor, path, columns[colnum - 1], True)
        else:
            path = (path[0] - 1,)
            if path[0] < 0:
                path = (len(treeview.get_model()) - 1,)
            gobject.idle_add(self.treeview.set_cursor, path, columns[-1], True)
        return True
    
    def key_tree_Tab(self, treeview, event):
        path, col = self.treeview.get_cursor()
        if not path:
            return False
        ## only visible columns!!
        columns = [c for c in self.treeview.get_columns() if c.get_visible()]
        colnum = columns.index(col)
        if colnum + 1 < len(columns):
            #cell = col.get_cell_renderers()[0]
            #cell.emit('edited', path, )
            #self.treeview.set_cursor( path, columns[colnum + 1], True)
            #gobject.idle_add(self.treeview.set_cursor, path, columns[colnum + 1], True)

            next_column = columns[colnum + 1]
            next_field_name = next_column.get_data('field_name')
            gobject.idle_add(self.treeview.set_cursor, path,
                             next_column, self.get_direct_edit(next_field_name) )
        else:
            tmodel = self.treeview.get_model()
            titer = tmodel.iter_next(tmodel.get_iter(path))
            if titer is None:
                titer = tmodel.get_iter_first()
            path = tmodel.get_path(titer)
            
            next_column = columns[0]
            next_field_name = next_column.get_data('field_name')
            gobject.idle_add(self.treeview.set_cursor, path, next_column,
                             self.get_direct_edit(next_field_name) )
        return False
    
    def key_tree_ctrl_n(self, treeview, event):

        if not 'i' in self.mode:
            self.sb(_("Insertion of new records is disabled. Sorry"))
            return
        try:
            self.record_new(treeview)
        except exc.ValidationError, e:
            return True

        return False
        
    def key_tree_ctrl_c(self, treeview, event):

        if not self.modelproxy.is_tree():
            return
        if not 'i' in self.mode:
            self.sb(_("Insertion of new records is disabled. Sorry"))
            return
        try:
            self.record_new(treeview, child=True)
        except exc.ValidationError, e:
            return True

        return False
        
    def key_tree_ctrl_s(self, treeview, event):

        if self.current in self.session.new and 'i' not in self.mode:
            self.sb(_("Insertion of new records is disabled. Sorry"))
            return

        if self.current in self.session.dirty and 'u' not in self.mode:
            self.sb(_("Update of records is disabled. Sorry"))
            return

        try:
            self.record_save()
        except exc.ValidationError:
            pass
        return False
        
    def key_tree_ctrl_k(self, treeview, event):

        if self.current not in self.session.new and 'd' not in self.mode:
            self.sb(_("Deletion of records is disabled. Sorry"))
            return False

        self.record_delete(treeview)
        return False
    
    def key_tree_ctrl_x(self, treeview, event):
        
        return self.key_tree_ctrl_k(treeview, event)
    
    def key_tree_ctrl_r(self, treeview, event):

        if  'b' not in self.mode:
            self.sb(_("browsing of new records is disabled. Sorry"))
            return

        self.reload_cb(treeview)
        return True
    
    def key_tree_Down(self, treeview, event):

        if self.modelproxy.tree_field_name:
            return False
        else:
            row = self.get_selected_path()
            if row is None:
                row = -1
            else:
                row = row[0]
            if row + 1 == self.len_model():
                try:
                    self.record_new(treeview)
                except exc.CommitError, e:
                    return False
                except exc.ValidationError:
                    return True

            return False

    def key_entry_ctrl_n(self, widget, event):

        try:
            widget.emit('activate')
        except:
            ## CellTextView does not have activate signal
            pass
        self.record_new()
        return True

    def key_entry_Tab(self, widget, event):
        """
        Trigger the validation when moving around the cells
        """
        ksym = gtk.gdk.keyval_name(event.keyval)
        if ksym in ('Tab',):
#             ## FIXME: Down and Return should behave differently if the completion is visible
#             if ksym in ('Down'): # and widget.get_completion().get_property('visible'):
#                 return False

            if self.cell_entry and not self.cell_entry.is_valid():
                if not self.cell_validate():
                    return True

    def get_direct_edit(self, field_name):
        """
        return the next column and if browsing must enter in edit mode
        """
#        from datetime import datetime, date, time, timedelta
        if not self.is_editable(field_name):
            return False

        NO_EDIT = (bool,)

        if not self.mapper_info.fields[field_name]['type'] in NO_EDIT:
            return True
        return False
        
#### callbacks columns
    def editable_keypress_cb(self, widget, event):
        """
        Trigger the validation when moving around the cells
        """
        ksym = gtk.gdk.keyval_name(event.keyval)
        if ksym in ('Tab',):
            if self.cell_entry and not self.cell_entry.is_valid():
                if not self.cell_validate():
                    return True

    def record_new_child_cb(self, widget, event=None):
        """Save the record and invokes the validator before UPDATE/INSERT a record
        """
        try:
            self.record_new(parent=self._clicked_path)
        except (exc.DialogValidationError, exc.CancelledAction):
            return True
    
###### Saving
    def set_value(self, field_name, value, path=None, fkvalue=None, initial=False, shown=False):
        """
        Set ``value`` in the model for ``field_name`` at path (default self.current)

        :param field_name: the name of the field we want to set
        :param value: the value we want to set
        :param path: the modelstor path at which we want to set a value. Default is the edited object.
        :param fkvalue: the value is handled as a primary key.  Used from
              completion and from gui_fields/tablewidget
        :param initial: if initial=False, the possible ``on_change_hook`` is not called
        

        """
        ## note: self.current cannot be used. We don't want the currently selected obj
        ##       but the one that is to be saved. This operation can be triggered
        ##       by a change in selection in which case self.current already points
        ##       to the new selection
        if path is None:
            obj = self.get_current_obj()
        else:
            obj = self.get_obj_at_path(path=path)
        
        if not obj:
            return

        ## casting of value
        field = self.gui_fields[field_name]
        if self.is_fkey(field_name):
            value = field.clean_value(value, input_is_fkey=True, obj=obj)
        else:
            value = field.clean_value(value, obj=obj)
        if field.editable:
            field.set_value(value, initial=initial, obj=obj, update_widget=False)

        ## text would come up automatically but only after
        ## loosing the focus...
        if fkvalue:
            self.cell_entry.entry.set_text(fkvalue)
            self.cell_entry.valid = True
            self.cell_entry.value = value
            self.cell_entry.text = fkvalue
            self.fkey_value = fkvalue
        else:
            if value is not None and not self.is_fkey(field_name):
                ## editable, if any, points to the last used editable
                ## that may not be the one that belogs to field_name...
                if self.cell_entry and field_name == self.cell_entry.field_name:
                    #self.cell_entry.entry.set_text(str(value))
                    self.cell_entry.entry.set_text(self.gui_fields[field_name].format_value(value))

        if not initial:
            self.run_hook('on_change_value', value, fkvalue, field, field_name=field_name)

    def get_value(self, field_name, shown=False):
        """
        return the value of the cell **currently edited***
        The name is possibly misleading due to parallelism with
        mask. 

        shown: show the lookup value instead of the eal value
        """
        
        obj = self.get_current_obj()
        if obj is None:
            raise exc.NoCurrentObjError(_("no current obj: maybe no record has yet been edited"))

        if field_name == self.currently_edited_field_name:
            if self.cell_entry:
                text = self.cell_entry.get_text()
                if self.is_fkey(field_name):
                    if shown:
                    ## we can be here becouse a clean_value triggered it. So don't pass there a
                    ## second time. If you ask for 'shown' I give you shown.
                        return text
                    else:
                        #return self.gui_fields[field_name].clean_value(text, input_is_fkey=False)
                        return self.cell_entry.value
                else:
                    return self.gui_fields[field_name].clean_value(text)
        value = getattr(obj, field_name)

        if shown == True and self.is_fkey(field_name):
            return self.gui_fields[field_name].get_human_value(value)
        else:
            return value

    def record_display(self, index=None, check=False):
        """
        Display all records (appending them to modelproxy.modelstore)
        check=False  - not used here but present becouse is used in Mask
        """

        if index == None:
            self.modelproxy.fill_model(clear=True)
        # TIP: status bar message
        self.sb(_("Total N. of records: %s") % (len(self.records)), seconds=None)

    def record_has_changed(self):
        
        if self.edited_row_model_path is None:
            return False
        return sqlwidget.SqlWidget.record_has_changed(self)
    
    def record_save_new(self, origin=None, interactive=True):
        """
        Create a new record and copy all data from an origin

        :param origin: the obj that must be duplicated, it can also belong
             to a different session
        :param interactive: (boolean) if True start editing and use set_value
        :return: the new object

        This can be used as follows in a on_save_as hook::

            for row in old.righe:
                rel_table.record_save_new(origin=row, interactive=False)

        to copy all rows from one record to the other
        
        """

        orig_obj = origin or self.get_obj_at_path(self._clicked_path)
        path, new_obj = self.record_new(start=interactive)

        for field in self.gui_fields:
            if not field.pkey and field.persistent:
                value = getattr(orig_obj, field.field_name)
                if interactive:
                    self.set_value(field.field_name, value, initial=False)
                    # this way is alternative to editing directly, for some reason it
                    # deletes the first edited field::
                    #field.set_value(value, initial=False, obj=new_obj)
                else:
                    setattr(new_obj, field.field_name, value)
        self.run_hook('on_save_as', orig_obj, new_obj)
        return new_obj
    
    def record_save(self, discard_unchanged=False, discard_new=False, ask=False, skip_check=True):

        """save the record

        Detects if any editing has been done consulting self.edited_row_model_path set
        by text_editing_started_cb.

        see record_validate for constraint explanation

        :param discard_empty: when record_save is called by reload, an empty record
                       does not need validation
        :param ask: if True a dialog box will ask if you really want to save
        :param skip_check: (boolean) if ask=True and skip_check=True save_unsaved will skip check
                       of real need to save

        """

        if self.edited_row_model_path is None: # no editing done
            dbg.write('no self.edited_row_model_path, nothing to save', self.edited_row_model_path)
            return

        if ask:
            response = self.save_unsaved(skip_check=skip_check, proceed=False)

            if response == gtk.RESPONSE_CANCEL:
                raise exc.CancelledAction

            if response == gtk.RESPONSE_NO: 
                return True  # Only used in record_in_mask, better would be a exc.NegativeAnswer
            
        obj = self.get_current_obj()

        if discard_unchanged or (discard_new and obj in self.session.new):
            if not self.record_has_changed():
                self.sb(_('Nothing to save'))
                if obj in self.session.new:
                    self.commit_inhibited = True
                    ## removing the modelproxy.modelstore element triggers edited_cb
                    ## so I need to set the path to None to prevent errors
                    path = self.edited_row_model_path
                    self.edited_row_model_path = None
                    self.modelproxy.modelstore.remove(self.modelproxy.modelstore.get_iter(path))
                    self.commit_inhibited = False
                    self.session.expunge(obj)
                    self.records.remove(obj)
                    self._new_record = False
                del obj
                self.last_new_obj = None
                self.edited_row_model_path = None
                return

        ## if the obj is new, you need to validate it anyhow: it was not changed but didn't start
        ## from a validated point    
        if not self.record_has_changed() and obj not in self.session.new:
            self.edited_row_model_path = None
            return

        self.record_validate(obj)
            
        ## in m2m case we don't want to commit now. We would trigger a commit of the
        ## record represented in the SqlMask that may not yet be validated

        if self.relationship_leader and (
            self.relationship_leader.current in self.session.new):
            # TIP: when saving m2m, we delay till leader record will be saved
            self.sb(_('delaying saving when main record will be saved'))
            self.delayed = True
        else:
            try:
                self.commit()
                self.totals.compute()
            except exc.HandledRollback, e:
                iter = self.modelproxy.modelstore.get_iter(self.edited_row_model_path)
                self.edited_row_model_path = None
                self.modelproxy.modelstore.remove(iter)
                self.sb(_("Record has NOT been saved"), seconds=100)
            self.delayed = True
            
        self.last_new_obj = None
        self._new_record = False

        if not self.delayed:
            self.session.expire(self.current)
            if self.relationship_leader:
                self.session.expire(self.relationship_leader.current)
                self.relationship_leader.record_display(check=False, delay_message=2)

    def record_new(self, widget=None, view_name='main', start=True, obj=None, parent=None, *args):
        """Add a new record

        :param widget: the treeview
        :param view_name: the name on the view
        :param start: start editing the first non default field
        :param obj: 
        :param parent: if defined it's a tuple representing a path.
                      The new row must be a child of ``parent``
        
        """
        ## I want to avoid generating a new obj if an object was created 
        ## and not modified (as when you press Down Arrow several times
        ## beyond the lower row)
        if not self.record_has_changed():
            #if self.last_new_obj:
            if (self.current and self.current in self.session.new) and self._new_record:
                self.sb(_("Already at new record"))
                return
        self.record_save()
        self.treeview.get_toplevel().set_focus(None)

        self.last_new_obj = self.get_new_object(obj=obj)
        # focus the row & start editing

        ## scroll_to_cell will trigger selection_changed_cb
        ## when the new_obj has been added but not yet edited.
        ## we inhibit this 
        self.commit_inhibited = True

        treeiter = self._get_next_iter(self.last_new_obj, parent=parent)
        path = self.modelproxy.modelstore.get_path(treeiter)
        if start:
            self.views[view_name].start_editing(path)
        ## set defaults
        if not obj:
            for field_name in self.field_list:
                self.gui_fields[field_name].set_default(obj=self.current)

        self.records += [self.last_new_obj]  ## adding to records is vital to get
                                             ## fk correctly, in case 
                                             ## this table is a M2M of M2O
        self.commit_inhibited = False
        self._new_record = True
        self.emit('record-new')
        return path, self.last_new_obj

    def record_add(self, obj, parent_path=None):
        """
        Add a record to the SqlTable

        :param obj: the object to be added
        :param parent_path: a possible path of the parent
        :returns: the new path
        """
        
        sqlwidget.SqlWidget.record_add(self, obj)
        path, obj = self.record_new(obj=obj, start=False, parent=parent_path)
        self.edited_row_model_path  =  path
        self.select_path(path)
        self.record_save()
        self.totals.compute()
        return path
        
    def unsaved_changes_exist(self, skip_check=False, skip_new=False):
        """collect possible changes and test if save is needed

        :param skip_check: we already know it needs saving. Passed to unsaved_changes_exists
        :param skip_new: skip_new may be an object whose changes we disregard (see unsaved_changes_exist)
        :return: False if cancel is pressed
        
        """

        if not skip_check and not self.record_has_changed():
            if self.last_new_obj:
                self.session.expunge(self.last_new_obj)
                del self.last_new_obj
                self.last_new_obj = None
                
        return sqlwidget.SqlWidget.unsaved_changes_exist(self, skip_new=skip_new)
        
    def record_delete(self, widget=None, interactive=True):
        """
        Delete a row and corresponding record
        """
        if self.ro:
            return True

        if not self.get_selected_obj():
            self.sb(_('No record selected'))
            return True

        sel = self.treeview.get_selection()
        model, paths = sel.get_selected_rows()

        if interactive:
            text = _("Delete this record?\n(%s)") % self.current
            iter = model.get_iter(paths[0])
            if model.iter_has_child(iter):
                text += "\n" + _("All children will be deleted as well") 
            response = self.dialog(type='ok-cancel', text=text)
            if response == gtk.RESPONSE_CANCEL:
                return

        self.deleting_row = True

        def do_del(model, path, iter):
            """
            potentially can delete a selection of many rows
            """
            ## Recursively delete all children, if any
            if model.iter_has_child(iter):
                for i in range(model.iter_n_children(iter), 0, -1): # backward
                    it = model.iter_nth_child(iter, i-1)
                    do_del(model, model.get_path(it), it)

            obj = model[path][0]
            deleted = True
            
            if self.relationship_mode == 'SINGLE':
                if obj in self.session.new:
                    self.session.expunge(obj)
                else:
                    self.session.delete(obj)
                #self.session.flush([obj])
                try:
                    self.commit()
                except exc.HandledRollback, e:
                    deleted = False
                        
            else:
                ## we're in M2M relationship or equivalent:
                ## we don't want to delete the object, just delete the relationship
                ## with the referred father
                if obj in self.session.new:
                    self.session.expunge(obj)

            if deleted:
                self.edited_row_model_path = None
                model.remove(iter)
                self._new_record = None
                if obj in self.records:
                    self.records.remove(obj)
        
        sel.selected_foreach(do_del)

        ## select the same row or the preceding
        row_n = paths[0][0]  # path is a tuple here
        if row_n >= len(model):
            row_n -= 1

            
        if len(model):  # prevent warning for empty models
            sel.select_path(row_n)
        
        self.deleting_row = False
        self.totals.compute()
        
        self.sb(_("Total N. of records: %s") % len(self.records), seconds=None)
        return True
    
    def record_delete3(self, item):
        """
        Delete a record clicked with left click from menu item. In this case
        self._clicked_obj is used rather than selected one.
        """
        
        self.select_path(obj=self._clicked_obj)
        self.record_delete()

    def _get_next_iter(self, new_obj, parent=None):
        """
        create a new row in the next reasonable place:

          * the next row for simple liststores
          * the next sibling for treestores

        :param new_obj: the obj to be placed there
        :param parent: if defined it's the path of the parent row for the new object 
          
        """
        path = parent or self.get_selected_path() or getattr(self, '_clicked_path', None) 
        if not path:
            try:
                return self.modelproxy.modelstore.append([new_obj])
            except TypeError:
                return self.modelproxy.modelstore.append(None, [new_obj])
        else:
            current_iter = self.modelproxy.modelstore.get_iter(path)
            if parent:
                new_iter = self.modelproxy.modelstore.insert_after(current_iter, None, [new_obj])
                self.treeview.expand_row(path, True)
                return new_iter
            parent_iter = self.modelproxy.modelstore.iter_parent(current_iter)
            if parent_iter:
                new_iter = self.modelproxy.modelstore.insert_after(parent_iter, current_iter, [new_obj])
            else:
                try:
                    return self.modelproxy.modelstore.insert_after(current_iter, [new_obj])
                except TypeError:
                    return self.modelproxy.modelstore.insert_after(None, current_iter, [new_obj])

        return new_iter
    
###### Validation
    def cell_validate(self):
        """Validate cell value and invoke field.set_value() or invoke completion.
        Return True if ok.
        
        The cell to be validated is the last visited cell, ie: the one whose
        field_name, path and cell where set inside text_editing_started_cb
        ForeignKey that do not validate should trigger completion

        This must be called by:
          - Return
          - Tab
          - Button1 on other cell
          - edited callback

        IMPORTANT: validation is not a way to enforce True validation. This bypasses
        normal completion mechanism!!!

        """
        new_text = self.cell_entry.get_text()
        field_name = self.currently_edited_field_name

        if self.relationship_mode == 'm2m' and not self.m2m_editable:
            # in m2m we don't want to edit this field but just to add/remove objects
            # I'm not sure if this should change
            if not new_text:
                return True

            try:
                # The next statement sets a value even if it could not pass completion!!!
                self.set_current(filter_by={field_name :new_text})
                return 
            except (exc.NoResultFound, exc.MultipleResultsFound), e:
                ## if there's no match, try completion
                dbg.write("No match: try completion")
                show = self.gui_fields[field_name].widget.completion.show_possible_completion
                show(self.cell_entry.entry, 'start')
                return True
            except (sqlalchemy.exceptions.DBAPIError), e:
                self.sb(e)
                return True
        else:
            ##
            if self.is_fkey(field_name):
                if self.cell_entry and self.cell_entry.is_valid():
                    return True
                if not new_text:
                    # casting '' to None => you're not allowed to use '' as FK...
                    self.set_value(field_name, None, initial=False)
                    # self.gui_fields[field_name].set_value(None, initial=False,
                    #                                       obj=self.current)                    
                    return True
                self.sb(_('Value is not valid, trying completion'))
                show = self.gui_fields[field_name].widget.completion.show_possible_completion
                show(self.cell_entry.entry, 'start', sb=False)
                return False
            else:
                try:
                    if self.cell_entry.text == new_text:
                        return True
                    self.set_value(field_name, new_text, initial=False)
                    # self.gui_fields[field_name].set_value(new_text, initial=False,
                    #                                       obj=self.current)
                    # A hook in "on_change_value" may trigger a deletion of cell_entry
                    # e.g. a totals.compute(), so let's check again
                    if self.cell_entry:  
                        self.cell_entry.text = new_text
                        self.cell_entry.valid = True
                    return True
                except exc.ValidationError, e:
                    self.cell_entry.valid = False
                    self.sb(str(e), seconds=8)
                    return False
        
        
    def length_control(self, wdg, field_name):
        if self.mapper_info.fields[field_name]['type'] is not str:
            return False
        length = self.mapper_info.fields[field_name]['length']
        text = wdg.get_text()
        lstr = len(text)
        if length:
            if lstr > length :
                wdg.set_text(re.sub('.$', '', text))
                # TIP: check in input field length %s %s -> field_name length
                self.sb(_("Input exceeded max %s length (%s)") % (field_name,length))
                return True
        return False

    def fkey_is_valid(self, field_name):
        """
        return True if current editable -if exists- has a value that does not need validation
        """
        if self.cell_entry and self.cell_entry.is_valid():
            return True
        return False
    

###### Record browsing 
    def initialize_record_editing(self, path, force=False, obj=None):
        """
        register the path of the editing and initialize all validation fields
        called when entering a new row or when a new record is added in m2m
        """
        # in Masks this is done when set_field is used on record_display
        # here the display is automatic via set_cell_data_func so we have to set
        # initial value when starting editing a record
        if not self.edited_row_model_path or force:
            if not obj:
                obj = self.get_selected_obj()
            if obj:
                for field in self.gui_fields:
                    if field.persistent: # only mapped fields need initialize
                        value = getattr(obj, field.field_name)
                        self.gui_fields[field.field_name].set_value(value, obj=obj, initial=True)

        self.edited_row_model_path = path
        
    def clear(self, *args, **kwargs):

        self.modelproxy.modelstore.clear()
    
    def reload_cb(self, widget, *args):
        """
        this is the real callback: C-r and toolbutton 
        """

        self.grab_focus(widget)
        
        if hasattr(self, 'filter_panel'):
            self.filter_panel.reload_cb(None)
        else:
            self.reload()
    
    def reload(self, *args, **kwargs):

        try:
            self.record_save(discard_unchanged=True)
        except exc.ValidationError:
            return
        
#        self.session.clear()
        self.commit_inhibited = True
        self.clear()
        start_time=datetime.datetime.now()

        ret = sqlwidget.SqlWidget.reload(self, *args, **kwargs)
        self.edited_row_model_path = None
        self.commit_inhibited = False
        self.totals.compute()
        self.cell_entry = None
        end_time=datetime.datetime.now()
        delta=end_time-start_time
        msg = "Startup: %s,%s secondi" % (delta.seconds, delta.microseconds/100000)
        self.sb(msg, seconds=3)
        self.session.rollback()
        if self.get_selected_obj() or len(self.records):
            self.emit('context-changed', self.get_selected_obj() or self.records[0])

        self._new_record = False
        return ret
                                         
    def record_refresh(self):
        """
        when self.refresh is called other programs have selected the records
        """
        self.edited_row_model_path = None  # must be set *before* clear()
                                # to inhibit selection_changed_cp
        self.modelproxy.fill_model(clear=True)
                
        self.totals.compute()
        self.treeview.columns_autosize()
        sqlwidget.SqlWidget.record_refresh(self)
        if self.get_selected_obj() or len(self.records):
            self.emit('context-changed', self.get_selected_obj() or self.records[0])
        self._new_record = False


    def record_in_mask(self, widget=None):
        """
        Open a SqlMask to show self.current if any and to follow selection.
        
        Hooks are set on the newly created mask so that validation is retained
        Remember to set any possible configuration of the table in an ``on_init``
        hook so that it will be propagated.

        If there are pending modification, a save dialog is opened. This function is normally
        invoked by the first menu entry of the menu popped by right click on a table *view this
        record in a mask*.

        :param widget: the menu entry that invoked it, can be ignored when calling it by hand
        :returns SqlMask: the SqlMask widget
        """
        from sqlkit.widgets import SqlMask, SqlTable
        try:
            quit = self.record_save(ask=True, skip_check=False)
        except exc.CancelledAction:
            quit = True
        if quit: 
            self.sb(_('Unsaved data prevent opening a Mask to show the (unsaved) record'))
            return

        if hasattr(self, '_mask'):
            self._mask().widgets['Window'].present()
            return
        mask = SqlMask(self.mapper, session=self.session, layout=self.layout,
                       metadata=self.metadata, dbproxy=self.dbproxy, hooks=self.hooks)
        mask.set_mode(self.mode, reset=True)
        mask.mode = '-bd'
        obj = getattr(self, '_clicked_obj', self.get_selected_obj())
        try:
            del self._clicked_obj
        except AttributeError:
            pass
        
        self.select_path(obj=obj)
        mask.set_records([obj])
        ## update value in the table, when updated in mask
        def update_table_treeview(mask, table):
            # emitting a 'row-changed', forces the update of the treeview 
            model = self.modelproxy.modelstore
            path = table.get_selected_path()
            if path: # seems selection sometimes is lost
                model.emit('row-changed', path, model.get_iter(path))
        record_save_id = mask.connect('record-saved', update_table_treeview, self)

        def disconnect_table(table, id):
            mask.disconnect(id)

        self.connect('delete-event', disconnect_table, record_save_id)

        ## signals to keep selection in sync 
        def follow_selection(table, obj, mask):
            if mask.record_has_changed():
                mask.record_save(ask=True)
            mask.set_records([obj])

        handler_id = self.connect('context-changed', follow_selection, mask)

        def disconnect(mask, id):
            self.disconnect(id)
            del self._mask

        mask.connect('delete-event', disconnect, handler_id)

        self._mask = weakref.ref(mask)
        return mask

    def fkey_record_in_mask(self, widget=None, field_name=None):
        """
        Open a SqlMask to show the fkey of this field

        :param widget: the menu entry that invoked it, can be ignored when calling it by hand
        :param field_name: the foreign key attribute name that should be displayed
        :returns SqlMask: the SqlMask widget
        """
        from sqlkit.widgets import SqlMask, SqlTable

        if not field_name and not hasattr(self, '_field_name'):
            return

        field_name = field_name or self._field_name

        ftable = self.completions[field_name].table

        mask = SqlMask(ftable.name, session=self.session, dbproxy=self.dbproxy, 
                       metadata=self.metadata, 
                       layout_nick=self._fk_layout_nick.get(field_name, 'default'),
                       )
        mask.set_mode(self.mode, reset=True)
        mask.mode = '-b'
        obj = getattr(self, '_clicked_obj', self.get_selected_obj())

        if obj:
            mask.set_records(pk=getattr(obj, field_name))

        ## signals to keep selection in sync 
        def follow_selection(table, obj, mask):
            if obj and self.get_selected_obj():
                if mask.record_has_changed():
                    mask.record_save(ask=True)
                mask.set_records(pk=getattr(self.get_selected_obj(), field_name))

        handler_id = self.connect('context-changed', follow_selection, mask)

        def disconnect(mask, id):
            self.disconnect(id)
            if hasattr(self, '_fmask'):
                del self._fmask

        mask.connect('delete-event', disconnect, handler_id)

        self._fmask = weakref.ref(mask)  # just for debug
        try:
            del self._field_name
            del self._clicked_obj
        except AttributeError:
            pass
        return mask

    def set_fk_layout(self, field_name, layout_nick):
        """
        set a layout to be used if opening a mask to edit the foreign key

        :param field_name: the field_nme of the column
        :param layout_nick: the nick name of the layout to be used a 'layout_nick'
        """
        self._fk_layout_nick[field_name] = layout_nick
            

    def upload_image(self, action, field_name=None):
        """
        Open a dialog to upoad a file and check if destination already exists.
        Setup for a copy when record will be saved
        """

        field_name = field_name or self._field_name
        dialog = dialogs.OpenDialog(title=_('Upload image'), default_filename='')
        filename = dialog.filename
        if not filename:
            return
        self.initialize_record_editing(self._clicked_path)
        self.select_path(self._clicked_path)
        save_path = self.gui_fields[field_name].get_save_path(
                        name=dialog.new_filename or filename,
                        obj=self.current)
        if os.path.exists(save_path):
            response = self.dialog(
                type="ok-cancel",
                text=_("A file with name '%s' already exists.\nOverwrite?") % save_path,
                title=_('Upload name duplication'))
            if response == gtk.RESPONSE_CANCEL:
                return

        self.gui_fields[field_name].widget.copy_file = filename # delay the real copy
        self.gui_fields[field_name].widget.new_filename = dialog.new_filename
        self.set_value(field_name, save_path)

        return save_path
    
    def upload_file(self, action):
        print action
    
    def delete_file(self, action, field_name=None):
        field_name = field_name or self._field_name
        self.initialize_record_editing(self._clicked_path)
        self.set_value(field_name, None)
    
    def show_file(self, action, field_name=None):

        from sqlkit.layout import image_widget
        
        field_name = field_name or self._field_name

        self.select_path(self._clicked_path)
        self.initialize_record_editing(self._clicked_path, force=True,
                                       obj=self.get_obj_at_path(self._clicked_path))
        # if you don't select it, the table mix up values of different rows, probably
        # _clicked_path gets used in wrong ways...
        filename = self.gui_fields[field_name].get_value(complete_path=True)
        if not os.path.exists(filename):
            self.message(text=_("File '%s' is not present in the filesystem" % filename),
                                type='error')
            return
        if not self.gui_fields[field_name].is_image(filename):
            open_file(filename)
            return
        w = gtk.Window()
        image = image_widget.ImageWidget()
        image.props.width = 700
        image.props.height = 700
        w.add(image)
        w.show_all()
        
        def change_file(table, obj):
            if obj:
                try:
                    img_path = table.gui_fields[field_name].get_value(complete_path=True)
                except exc.NoCurrentObjError, e:
                    if table.records:
                        table.select_path((0,))
                        img_path = table.gui_fields[field_name].get_value(complete_path=True)
                    else:
                        img_path = None
                        
                image.set_image(img_path)

        change_file(self, self.current)
        self.connect('context-changed', change_file)

    def save_file(self, action, field_name=None):

        import shutil
        
        field_name = field_name or self._field_name
        self.initialize_record_editing(self._clicked_path)
        orig_filename = self.gui_fields[field_name].get_value(complete_path=True)
        dialog = dialogs.SaveDialog(default_filename=os.path.basename(orig_filename))
        if dialog.filename:
            shutil.copyfile(orig_filename, dialog.filename)

###### Misc
    def get_selected_path(self):
        """Return the path of the selected row or None

        NOTE: treeselection 'changed' signal arrives when the selection change has
              already occurred. Use :attr:`edited_path` to get the path that
              is being currently edited

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
    
    def get_current_obj(self):
        """
        Return the corrently edited (not just selected!!) obj or obj at path.
        Selection can already be elsewhere (as in on_selection_change)
        Read comment in set_value
        Return None if no selection
        """
        path = self.edited_row_model_path

        if path is None:
            #return None
            return self.get_selected_obj()
        else:
            obj = self.modelproxy.modelstore[path][0]
            return obj

    def get_selected_obj(self):
        """Return the corrently selected obj. Return None if no selection"""
        path = self.get_selected_path()

        if path is None:
            return None
        else:
            obj = self.modelproxy.modelstore[path][0]
            if not isinstance(obj, self.mapper.class_):
                return None
            return obj

    def get_obj_at_path(self, path, all=False):
        """
        Return the object at path. Return None if no selection.
        If the object at path is a total object (see :ref:`totals`) it
        will be discarder unless you use param all=True

        :param path: the modelproxy.modelstore path
        :param all: boolean: only return object of the main class (no totals)
        """
        obj = self.modelproxy.modelstore[path][0]
        if isinstance(obj, self.totals.total_class):
            return None
        return obj

    current = property(get_current_obj)

    def set_current(self, pk=None, filter_by=None):
        """
        retrieve object with primary key pk and set it as current object
        ie: in the row currently selected
        This is mainly used in completion callback for m2m relationship_mode
        """
        
        ## I really need not to flush, since in this moment there is a new object in the
        ## row that started completion that is not ready for flushing
        ## more: it may be due for substitution!!

        path = self.get_selected_path()
        assert path is not None
        
        obj = self.get_record_no_flush(pk=pk, filter_by=filter_by)

        expired_obj = self.modelproxy.modelstore[path][0]
        if expired_obj in self.session:
            self.session.expunge(expired_obj)
        self.records.remove(expired_obj)

        ## assigning modelproxy.modelstore value will trigger 'editing-canceled'
        self.cell_entry.substitute = True
        self.cell_entry.valid = True
        self.modelproxy.modelstore[path][0] = obj
        
        if not (self.relationship_mode == 'm2m' and not self.m2m_editable):
            path = self.edited_row_model_path
            self.initialize_record_editing(path, force=True, obj=obj)

        self.records += [obj]

    def get_record_no_flush(self, pk=None, filter_by=None):
        """
        Get the record in a way so that no flushing is performed
        """
        query = self.session.query(self.mapper).autoflush(False)
        if pk:
            obj = query.get(pk)
        elif filter_by:
            obj = query.filter_by(**filter_by).one()
        return obj
        
    def set_opts(self, icons=True, scroll='xy', width=None):
        """
        Modify default appearance of some features:
        
        :param scroll: eliminate scrollbars (values: x|y|xy|None)
        :param icons: allows to disable icons in a m2m relationship
        :param width: set the maximum width of the widget

        :type icons: boolean
        :type scroll: boolean 
        """
        if not icons:
            self.widgets['A.icons'].hide()
        if not scroll:
            self.widgets['S=tree'].set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        else:
            if 'x' not in scroll:
                xpolicy = gtk.POLICY_NEVER
            else:
                xpolicy = gtk.POLICY_AUTOMATIC
            if 'y' not in scroll:
                ypolicy = gtk.POLICY_NEVER
            else:
                ypolicy = gtk.POLICY_AUTOMATIC
                
            self.widgets['S=tree'].set_policy(xpolicy, ypolicy)

        if width:
            self.treeview.set_property('width_request', width)
            
    def export(self, menuItem, view_name='main'):
        """
        export visible data in csv format
        """
        
        def foreach_handler(model, path, iter, ret):
            ## NOTE: when this function return a True value, iteration terminates!!!
            obj = model.get_value(iter, 0)
            view = self.views[view_name]
            field_list = [c.get_data('field_name') for c in view.treeview.get_columns()
                          if c.get_property('visible')]
                          
            ## getattr(obj, f, obj): obj is used when the column does not have a 1-1 mapping
            ## to an attribute as happens for FunctionColumn that show a function out of the
            ## record
            ret += [[self.gui_fields[f].get_human_value(getattr(obj, f, obj)) for f in field_list ]]

        def get_all_rows():
            ret = []
            self.modelproxy.modelstore.foreach(foreach_handler, ret)
            return ret

        dialog = ExportDialog(get_all_rows, title=_("Export in csv file"),
                              default_filename="%s-export.csv" % self.nick)

        return 

    def select_path(self, path=None, obj=None):
        """
        Select path ``path``. If path is null and obj is not null try finding path at which is obj


        :param path:  the path to be selected or None
        :param obj:  if path is None, the object to be searched for and selected
        """

        return self.views['main'].select_path(path=path, obj=obj)
            
    def add_record(self, obj):
        """
        Add record to the model and setup all what is needed

        :param obj: an object of type ``table.mapper.class_``
        """
        self.records += [obj]
        try:
            self.modelproxy.modelstore.append([obj])
        except:
            self.modelproxy.modelstore.append(None, [obj])
        self.session.add(obj)
#        self._record_new
        self.totals.compute()

    def len_model(self, model=None):

        a = [0]
        if not model:
            model = self.modelproxy.modelstore

        def count(model, path, iter, counter):
            counter[0] += 1

        model.foreach(count, a)

        return a[0]
                
    def add_row_filter(self, func):
        """
        Add a filter that selects which rows should be displayed

        :param func: the function that will be called with the obj as argument
                     and must return a bool
        """
        self.modelproxy._filter_rows = True
        self.modelproxy._check_func = func
        
#### completion

    def set_editable(self, editable=True):
        """
        Turn this table into a normal editable table.
        A tables is not normally editable if it has ``relationship_mode = m2m``

        :param editable: Only meaningful for table that represent an
               m2m relationship: turns the table from non editable to editable, 
               read the explanation in :ref:`relationships`
        :type editable: boolean
        """
        self.m2m_editable = editable
        for field in self.gui_fields:
            field.widget.add_completion(editable=editable)
        
class ExportDialog(dialogs.SaveDialog):

    FILTER_FILES = (
        ( _('Csv files'), '*.csv'),
        ( _('All files'), '*.*'),
        )

    DELIMITER = ','
    QUOTE = None
    DIALECT = 'excel'

    def __init__(self, get_rows_func, *args, **kwargs):
        """
        A dialog to export data into a csv file

        :param get_rows_func: a function to be called by  csv.writer.writerows
        :param default_filename: the default
        """

        self.get_rows_func = get_rows_func
        dialogs.SaveDialog.__init__(self, *args, **kwargs)
        
    def write(self):

        import csv

        filename = self.dialog.get_filename()
        f = open(filename, "wb")
        writer = csv.writer(f, dialect=self.DIALECT,
                            delimiter=self.DELIMITER,
                            quoting=self.QUOTE or csv.QUOTE_MINIMAL)
        writer.writerows(self.get_rows_func())
        f.close()

