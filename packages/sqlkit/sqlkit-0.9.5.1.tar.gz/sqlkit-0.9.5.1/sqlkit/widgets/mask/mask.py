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

import re
import datetime
import decimal

import gtk
import gobject

from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm.exc import ObjectDeletedError

import sqlkit
from sqlkit import debug as dbg, exc, _, layout, fields
from sqlkit.widgets.common import completion, sqlwidget

FK_COLOR = gtk.gdk.color_parse('navyblue')
LBL_HOOVER_STYLE = gtk.gdk.color_parse('red')

class SqlMask(sqlwidget.SqlWidget):
    """
    SqlMask is the widget that displays one record at a time and buttons to
    browse data, save/delete records. SqlMask is inherited from
    :class:`sqlkit.widgets.common.sqlwidget.SqlWidget`
    
    """

    __metaclass__ = None if not dbg.debug else dbg.LogTheMethods
    labels   = None  # correspondance Label <-> EventBox
    row_count = 0    # number of records in the mapper
    current_idx = 0
    current = None
    current_mode = None
    __gsignals__ = {
        'pre-display' : (gobject.SIGNAL_RUN_LAST,
                         gobject.TYPE_BOOLEAN,
                         # 
                         (gobject.TYPE_PYOBJECT,),
                         ),
        }


    def __init__(self, *args, **kw):
        """
        Prepare for a new record
        """
        #current_idx = dbg.TraceIt(0, name='current_idx', mode='rw')

        sqlwidget.SqlWidget.__init__(self, *args, **kw)
        ## idle so that possible defaults get a chanche to be effective
        gobject.idle_add(self.record_new_idle)
        self.run_hook('on_init')

###### Filters/constraints
###### Layout
    def _get_layout(self, lay, naked):

        self.lay_obj, self.widgets  = sqlwidget.SqlWidget._get_layout(self, lay, naked)

        self._add_click_for_filter()
        self._add_color_to_labels()
        self._add_tips()
        self._add_wheel_support()
        
        return self.lay_obj, self.widgets  
        
    def _add_wheel_support(self):
        """
        add mouse wheel support
        """
        if not self.widgets['Window']:
            return
            
        def scroll_event_cb(widget, event):
            if not self.actiongroup_browse.get_sensitive():
                return
            
            if event.direction == gtk.gdk.SCROLL_UP:
                return self.record_display(incr=-1)
            else:
                return self.record_display(incr=1)

        self.widgets['Window'].connect('scroll_event', scroll_event_cb)

    def _add_color_to_labels(self):
        """
        add bg colors and fonts to signal needed fields
        """

        def ene_cb(eb, ev):
            eb.get_child().set_state(gtk.STATE_PRELIGHT)
            return True

        def lne_cb(eb, ev):
            eb.get_child().set_state(gtk.STATE_NORMAL)
            return True

        for field_name in self.mapper_info.fields.keys():
            if field_name in self.labels:
                lbl    = self.labels[field_name]
                ev_wdg = self.labels[field_name].parent

                ev_wdg.connect('enter-notify-event', ene_cb)
                ev_wdg.connect('leave-notify-event', lne_cb)
                lbl.modify_fg(gtk.STATE_PRELIGHT, LBL_HOOVER_STYLE)

                ## label FK_COLOR to tell it's a foreign key
                if self.mapper_info.fields[field_name]['fkey'] :
                    #dbg.write("FK", field_name)
                    self.labels[field_name].modify_fg(gtk.STATE_NORMAL, FK_COLOR)
                else:
                    #dbg.write("NO", field_name)
                    pass

    def _add_tips(self):
        """
        Add tips to labels starting from label_map
        """

        for field_name, values in self.label_map.iteritems():
            label, help_text = values

            key = "l=%s" % field_name

            if label:
                if key in self.widgets:
                    self.widgets[key].set_text(label)

            if help_text:
                if key in self.widgets:
                    self.widgets[key].set_tooltip_text(help_text)

    def _add_click_for_filter(self):
        """
        make labels clickable for filter panel
        """

        ## all EventBox 
        self.labels = {}
        for field_name in self.mapper_info.fields.keys():
            lbl_name_wdg = "l=%s" % field_name
            if lbl_name_wdg in self.widgets:
                self.labels[field_name] = self.widgets[lbl_name_wdg]
                #dbg.write("%s -> %s"% (field_name, self.labels[field_name]))
            else:
                #dbg.write("Missing event_box for %s" % (field_name))
                pass
    
        ## add click that pops filter_panel
        for field_name, label in self.labels.iteritems():
            event_box = label.parent
            event_box.connect('button-press-event', self.button_press_event_cb, field_name)

    def _set_arrows_sensitivness(self, display_idx=None):
        """
        set sensitivness of back and forward arrows according to records length and position
        """
        if display_idx is None:
            display_idx = self.current_idx or 0

        self.ui_manager.get_action('/Main/Go/Forward').set_sensitive(display_idx+1 < len(self.records))
        self.ui_manager.get_action('/Main/Go/Back').set_sensitive(display_idx > 0)

    def setup_field_validation(self, field_list=None):
        """
        create fields.Field objects 

        gui_fields: validation fields
        --------------------------
        is a dict: 
           :key:   is the field_name
           :value: is a field from sqlkit.widget.mask.fields

        """
        ## gui_fields can be passed as argument of the class. In that case widgets
        ## used to represent the data are provided by another SqlMask

        if not self.gui_fields:
            raise Exception("I shouldn't be here...")
            self.gui_fields = {}

        field_chooser = fields.FieldChooser(self.mapper_info, self.widgets,
                                     gui_field_mapping=getattr(self, 'gui_field_mapping', None))

        for field_name, widget_key in self.laygen.fields_in_layout.iteritems():
            widget = self.widgets[widget_key]
            db_spec = self.mapper_info.fields.get(field_name, None)
            
            Field = field_chooser.get_field(field_name, db_spec, widget_key)
            field = Field(field_name, db_spec)

            field.set_master(self)
            # the widget may already be created (by layout.Layout)
            gtk_widget = self.widgets.get(widget_key, None)
            field.set_widget(gtkwidget=gtk_widget, def_str=widget_key)
            
            self.field_widgets[field_name] = field.widget
            self.gui_fields[field_name] = field
            
    def button_press_event_cb(self, widget, event, field_name):
        """
        callback of click on labels
        """
        if event.button == 3:
            self.show_field_info(None, field_name)
        else:
            self.filter_panel.add(widget, event, field_name, self)        
        
    def set_frame_label(self, frame_name, markup_label, opts='bi'):
        """
        Add a label to the frame whose key in self.widgets is 'frame_key'.

        :param frame_name: the key in :attr:`self.widgets`
        :param markup_label: the label with possible markup
        :param opts: a combination of b (bold) and i (italic). Default: 'bi'
        
        In example 15::

          LAYOUT = '''
           {|.number .. }
           ...
          '''
          
        m.set_frame_label('number', 'Number')
        """

        frame = self.widgets['F.%s' % frame_name]
        frame.set_label('a')

        if 'i' in opts or '':
            markup_label = "<i>%s</i>" % markup_label
        if 'b' in opts or '':
            markup_label = "<b>%s</b>" % markup_label

        frame.get_property('label-widget').set_markup(markup_label)
        
###### Actions/UiManager
    def prepare_actions(self):
        """
        Prepare action needed by UIManager
        """
        sqlwidget.SqlWidget.prepare_actions(self)

        self.actiongroup_insert.add_actions([
            ('New', gtk.STOCK_NEW,   None, '', _('Add new record'), self.record_new_cb),
            ('Save-as', gtk.STOCK_SAVE_AS, None, None, None, self.record_save_new_cb),
            ])
        self.actiongroup_select.add_actions([
            ('Undo', gtk.STOCK_UNDO, None, None, _('Discard changes'), self.record_undo_cb),
            # TIP Modify menu entry in the mask to reread a single record from database
            ('RefreshRecord', gtk.STOCK_REFRESH, _('Refresh this record'), None,
             _('Reread this record from db'), self.record_refresh_cb),
            ])
        self.actiongroup_delete.add_actions([
            ('Delete', gtk.STOCK_DELETE, None, '', _('Delete this record'), self.record_delete),
            ])

    def prepare_uimanager(self):
        """
        Prepare UIManager, actions, and accelerators
        """

        from sqlkit.widgets.common import uidescription
        
        sqlwidget.SqlWidget.prepare_uimanager(self)

        self.ui_manager.add_ui_from_string(uidescription.MASK_UI)


###### Saving
    def set_value(self, field_name, field_value, fkvalue=None, initial=False, shown=False):
        """
        set the value of any field present in ``gui_fields``. Uses field.set_value
        if ``initial`` is False, run ``on_change_value``
        

        :param  field_name: the field_name to be changed
        :param  field_value: the new value
        :param  fkvalue: a possible foreign key value. It's here just  for compatibility with SqlTable's one
        :param  initial: a boolean indicating if it's an initial value (passed to field)
        :param  shown: a boolean indicating if the  value is the displayed value (passed to field)
        
        """

        if field_name not in self.gui_fields:
            raise exc.FieldNotInLayout("field_name: %s" % (field_name))

        field = self.gui_fields[field_name]
        field.set_value(field_value, initial=initial, shown=shown)

        
        if not initial:
            fkvalue = fkvalue if fkvalue is not None else field.get_value(shown=True)
            self.run_hook('on_change_value', field_value, fkvalue, field, field_name=field_name)
    
    def get_value(self, field_name, shown=False):
        """
        return the value from the widget

        :param field_name: the field_name
        :param shown: boolean: true if the value we want is the dislayed one

        """

        if field_name not in self.gui_fields:
            dbg.write("%s Non in gui_fields %s" % (field_name, self.gui_fields.keys()))
            raise exc.FieldNotInLayout("field_name: %s" % (field_name))

        field = self.gui_fields[field_name]
        return field.get_value(shown=shown)

    def clear_value(self, field_name):
        """
        clear the value to the default value
        """
        if field_name not in self.gui_fields:
            raise exc.FieldNotInLayout("field_name: %s" % (field_name))

        self.gui_fields[field_name].set_default()
        
    def record_new(self, widget=None, clear=True):
        """
        prepare a new object and set
        clear = True/False. clear=False is used when 'saving as'
        """
        if self.current:
            if clear and not self.record_has_changed():
                if self.last_new_obj:
                    self.sb(_("Already at new record"))
                    return

        if clear:
            try:
                if self.current:
                    ## this is important to trigger validation in time to prevent
                    ## a change in self.current. No need if all we want is to
                    ## 'save as new'
                    self.record_save()
                self.clear_mask(check=False)
            except exc.ValidationError:
                return

        self._set_arrows_sensitivness()

        self.current = self.get_new_object()
        self.last_new_obj = self.current
        self.records += [self.current]
        self.current_idx = len(self.records) -1
        self.sb(_("New record %s") % (self.current_idx +1))
        if 'i' in self._mode:
            self.actiongroup_update.set_sensitive(True)
            
        ## the following lines ensure that in presence of
        ## related tables any 'related.records' is exactly 'current.related'
        ## (e.g. m.related.movies.records is m.current.movies).  This is
        ## important to use loops in a natural way when you add a record and
        ## want to loop on already written rows that are only present in the
        ## related table
        for key in self.related.keys():
            r = self.related[key]
            r.records = getattr(self.current, key)

        self.current_mode = 'INSERT'
        self.emit('record-new')
        
    def record_new_idle(self):
        """
        record_new has been asked with idle_add from __init__
        when no info on possible .reload() was available.
        create a new record only if no records are present
        """
        if not self.records:
            self.record_new()

    def record_undo_cb(self, menuItem):
        """
        undo possible modification to the mask
        """
        self.discard_changes()
        self.record_display(check=False)
        
    def record_refresh_cb(self, menuItem):
        """
        undo possible modification to the mask
        """
        self.discard_changes()
        if not self.current in self.session:
            return
        self.session.expire(self.current)
        try:
            self.record_display(check=False)
        except ObjectDeletedError:
            # TIP message issued when a refresh is done on a deleted record
            self.dialog(text=_('The record is no longer present in the database'))
            self.record_display_next()

    def record_mask2obj(self, obj=None, force=False):
        """
        collect data from the mask and set into the object if record_has_changed())
        force is used when saving a new obj as in record_new
        """
        if not obj:
            return obj

        if obj not in self.session: ## it should never happen, really... why do we need?
            self.session.add(obj)

        # mask2obj ensures that the object used for validation is updated from the mask
        # record_valildate that is run just after mask2object requires validation_errors/warnings
        # be present
        self.validation_errors = {}
        self.validation_warnings = {}

        if force or self.record_has_changed():

            for field in self.gui_fields:
                field_name = field.field_name
                try:
                    value = field.get_value()
                    if field.editable:
                        field.validate( value , clean=True)

                    if field.persistent:   # persisted fields, mask2obj has already cleaned  them
                        field.set_value(self.get_value(field_name), initial=False, obj=obj, update_widget=False)

                except exc.ValidationError, e:
                    self.add_validation_error(e, field_name=field_name)
                except exc.MissingWidget, e:
                    pass

        return obj

    def record_save_cb(self, widget, *args):
        """
        record save callback...
        """
        self.grab_focus(widget)

        try:
            self.record_save(None)
        except (exc.DialogValidationError, exc.CancelledAction), e:
            pass

    def record_save(self, ask=True, new_obj=False, *args):
        """
        invokes the validator before UPDATE/INSERT a record
        ask:  ask if save is required
        new_obj:   the record is new. It forces mask2obj to skip check and save all fields
        """
        focus_widget = self.get_toplevel().get_focus()
        if focus_widget and isinstance(focus_widget, gtk.Entry):
            focus_widget.activate()
        self.get_toplevel().set_focus(None)

        changed = self.record_has_changed()
        if changed or new_obj or (
            self.current in self.session.new and self.session.is_modified(self.current)
            ) or (self.unsaved_changes_exist(skip_new=self.current)):
            pass
        
        else:
            self.sb(_('Nothing to save'), seconds=4)
            return

        if ask:
            response = self.save_unsaved(skip_check=True, proceed=False)

            if response == gtk.RESPONSE_CANCEL:
                raise exc.CancelledAction

            if response == gtk.RESPONSE_NO: 
                return
            
        obj = self.record_mask2obj(self.current, force=new_obj)
                
        self.record_validate(obj, single_fields=False)
            
        try:
            self.commit()
        except exc.HandledRollback, e:
            return
            
        self.last_new_obj = None
        
        self.session.expire(self.current)
        self.record_display(check=False, delay_message=2)
        
    def record_save_new(self, obj=None, commit=True, ask=True):
        """
        create a new record by duplicating the obj
        :param obj: the obj to be cloned
        :param commit: (boolean) commit after duplicating
        :return: the new object
        """

        ## if PKey is editable we should add a check that is not the same
        if isinstance(self.tables, list):
            tbl = self.tables[0]
        else:
            tbl = self.tables
        pkey_changed = False

        for key in self.mapper_info.get_pkeys(tbl):
            if key in self.gui_fields:
                if self.is_editable(key):
                    if self.gui_fields[key].has_changed():
                        pkey_changed = True
            else:
                pkey_changed = True
                    
        if not pkey_changed:
            self.dialog(text=_("Primary key (%s) didn't change. Refusing to save as new" % key))
            return

        o2m_list = [name for name, table in self.related.iteritems()
                    if not table.relationship_mode == 'm2m']
        save_as_is_managed = self.hooks and getattr(self.hooks, 'on_save_as', None)
        if o2m_list and not save_as_is_managed:
            msg = "Tables expressing one to many relationship will be left empty (%s)\n" + \
                  "Read the docs for more informations"
            response = self.dialog(type='ok-cancel', text=_(msg) % o2m_list,
                                   icon='gtk-dialog-warning')
            if response == gtk.RESPONSE_CANCEL:
                return
        elif ask:
            msg = _("Do you want to copy all data to a new record?")
            response = self.dialog(type='ok-cancel', text=_(msg) % o2m_list,
                                   icon='gtk-dialog-question')
            if response == gtk.RESPONSE_CANCEL:
                return
            
        records_m2m = {}
        for table_name, table in self.related.iteritems():
            if table.relationship_mode == 'm2m':
                records_m2m[table_name] = table.records

        old_obj = self.current
        self.record_new(clear=False)

        for table_name, table in self.related.iteritems():
            if table_name in records_m2m:
                table.set_records(records_m2m[table_name])
            else:
                table.set_records([])

        obj = obj or self.current
        self.record_mask2obj(obj, force=True)
        for table_name, table in self.related.iteritems():
            setattr(obj, table_name, table.records)
            
        self.run_hook('on_save_as', old_obj, obj)

        ## record_refresh() is not really needed here. You should implement it
        #  in your own on_save_as, but you should know you need to...
        for table in self.related:
            if table.modelproxy.tree_field_name and not table.relationship_mode == 'm2m':
                table.record_refresh()

        if commit:
            try:
                self.record_save(ask=False)
            except exc.ValidationError, e:
                pass

        self.emit('record-selected', )
        return obj
       
    def record_delete(self, widget=None, interactive=True):
        """
        delete a record
        """
            
        if interactive:
            text = _("Delete this record?\n(%s)") % self.current
            response = self.dialog(type='ok-cancel', text=text)
            if response == gtk.RESPONSE_CANCEL:
                return
        obj = self.records[self.current_idx]
        if obj in self.session.new:
            self.session.expunge(obj)
        else:
            self.session.delete(obj)
        self.last_new_obj = None
        
        try:
            self.commit(_('Deleted'))
            self.emit('record-deleted', obj)
        except exc.HandledRollback, e:
            return
        self.record_display_next()
            
    def record_display_next(self):
        """Display the next (or previous) record after deleting a record
        """

        self.records.pop(self.current_idx)

        self.clear_mask(check=False)
        if not self.records:
            self.record_new()
        else:
            if self.current_idx  > len(self.records) -1:
                self.current_idx -= 1
            self.record_display(index=self.current_idx)
    
###### Validation
###### Record browsing 
    def reload(self, **kw):
        """
        Reload the data
        """
        changed = self.record_has_changed()

        if changed:
            skip_new = False
        else:
            skip_new = self.current
            
        response = self.save_unsaved(skip_check=changed, skip_new=skip_new)
        if response == gtk.RESPONSE_CANCEL:
            return
            
        self.current_idx = 0
        length = sqlwidget.SqlWidget.reload(self, **kw)
        if not length:
            self.record_new()
        self.set_mode()
        return length

    def record_display(self, record=None, incr=0, index=None, check=True, delay_message=0):
        """
        display an object record in the mask. Defaults to self.records[self.current + incr]

        :param record: the record to be displayed
        :param index:  the index in self.records to be displayed
        :param incr:   increment to current index
        :param check:  boolean. If False prevent checking if saving is needed
        :param delay_message: int. Number of seconds to wait before writing in the status bar.
               This is needed to prevent normal display message from hiding "Saved" message.
        """
        if not self.records:
            ## TIP: message in the statis bar
            self.sb(_('No record present'), seconds=5)
            return
        if check:
            try:
                self.record_save(ask=True)
            except (exc.CancelledAction, exc.DialogValidationError):
                return

        if index is not None:
            display_idx = index
        else:
            display_idx = (self.current_idx or 0) + incr 

        try:
            assert display_idx >= 0  # no negative indexes
            obj = self.records[display_idx]
            self.clear_mask(check=False)
            self.current_idx = display_idx
            self.current = obj
            msg_info = "%s/%s" % (display_idx +1, len(self.records))
        except (IndexError, AssertionError), e:
            msg_info = "%s/%s" % (self.current_idx +1, len(self.records))
            if incr >= 0:
                self.sb(_('Already last record') + msg_info)
            else:
                self.sb(_('Already first record') + msg_info)
            return None


        gobject.timeout_add(delay_message * 1000, self.sb, msg_info)

        self.emit('pre-display', obj)

        for field in self.gui_fields:
            if field.persistent:
            #if field.field_name in self.mapper_info:
                value = getattr(obj, field.field_name)
            else:
                value = field.clean_value(obj)
                
            self.set_value(field.field_name, value, initial=True)

        self._set_arrows_sensitivness(display_idx)
        self.emit('record-selected', )
        return True

    def set_records(self, records=None, index=0, pk=None):
        """
        set records to browse, and display number idx

        :param records: set records as self.records. records must be a list
        :param index: which record to display after settings self.records
        :param pk: display record with this PrimaryKey. The record is retrieved with
                   self.get_by_pk that doesnnot flush the session
        """
        self.clear_mask()

        if not records and pk:
            records = self.get_by_pk(pk)
            
        self.records = records or []
        # it's handy to set set_records([table.current])
        # that may also be empty
        if records and not records == [None]: 
            self.record_display(index=index)
        self.record_refresh()

    def clear_cb(self, accell_group, window, ord, flags):
        self.record_new()

    def clear_mask(self, check=True):
        """
        clear the mask for a new record
        NOTE: this does NOT prepare for a new record (missing obj)

        :param widget: 
        :param check:  boolean: false prevent a check
        """

        if check and not self.save_unsaved():
            return

        self.current = None
        
        for field in self.gui_fields:
            self.clear_value(field.field_name)

    clear = clear_mask
    
    def record_forward_cb(self, widget):
        """
        display the next record in the mapper"""

        self.grab_focus(widget)
        return self.record_display(incr=1)
    
    def record_back_cb(self, widget):
        """
        display the previous record in the mapper"""
        
        self.grab_focus(widget)
        return self.record_display(incr=-1)
    
####### Misc
    def get_widget(self, field_name):
        """
        get the widget that renders field_name
        """

        return self.gui_fields[field_name].widget.gtkwidget

    def get_current_obj(self):
        """
        Return the object that is currently edited
        """
        return self.current

    def fkey_is_valid(self, field_name):
        """
        return True if current editable -if exists- has a value that does not need validation
        """
        return self.gui_fields[field_name].widget.is_valid()



