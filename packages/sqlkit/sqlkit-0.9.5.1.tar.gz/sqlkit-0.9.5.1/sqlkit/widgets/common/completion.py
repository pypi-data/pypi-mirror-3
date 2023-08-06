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

Public API
==========

.. autoclass:: SimpleCompletion
   :members: autostart, force_enum, group_by, filtered_query, query, filter, set_values, attrs

.. autoclass:: FkeyCompletion

.. autoclass:: M2mCompletion


"""
import re
from copy import copy

import gtk
from gobject import markup_escape_text

from sqlalchemy import text, select, Table, exceptions
from sqlalchemy.sql import and_, or_, not_
from sqlalchemy.orm import class_mapper, mapper

import sqlkit
from sqlkit import debug as dbg, _, exc
from sqlkit.db.proxy import table2mapper
from sqlkit.db.utils import tables, get_description, DictLike
from sqlkit.db.django_syntax import django2query
from sqlkit.db import utils
from sqlkit.debug.sql import debug_inline_params

####### Completion
# EntryCompletion widgets are added on the fly triggered by F1, C-F1 or menu items
# select_values will get data from the db and fill a listore
# match_function filters using re.search from the listore to fill in the completion
#
OP = {
    'sqlite' : 'LIKE',
    'postgres'     : '~*',
    'postgresql'     : '~*',
    'mysql'  : 'ILIKE',
    }

class SimpleCompletion(object):
    """
    An object that hold all the information on how to retrieve possible completions in simple cases
    
    """
    __metaclass__ = None if not dbg.debug else dbg.LogTheMethods
    autostart = False
    autostart_last_length = 0
    
    VALUE_COL = 0
    DESCRIPTION_COL = 0
    MARKUP_COL = 0
    OBJ_COL = 1
    MATCH_COL = 2
    SEARCH_COL = 0
        
    group_by = None
    """
    The field_name on which the output should be grouped.
    ``field_name`` will be added to the request and used to group completion options.

    """

    autostart = None
    """A possible interger stating after how many chars completion should start automatically"""

    query = None
    """The query that will be issued upon completion request if ``Alt`` is pressed (i.e.: not
    all filters applied). You can add filters width :meth:`filter` or via SqlAlchemy syntax."""

    filtered_query = None
    """The query that will be issued upon completion request. You can customize it as for :attr:`query`"""

    force_enum = None
    "Modify output: show all options regardless of what has been already written in the field"

    column = None
    "the database column it will use when searching the values. It's a Sqlalchemy Column"

    attrs = None
    """a list of attributes that will be added to the object retrieved to fill the completion choices.
    You can add attributes if you need to have more data e.g. in :ref:`completion hooks <on_completion>`
    """

    def __init__(self, master, widget, field_name):

        """completion is the way we can find possible completions of text in
        a cell.  In case the edited field has a Foreign Key constraint
        completion will follow the table/field to retrieve the possible
        values, in case we don't have an fk, completion will suggest values
        already present in the db.

        A completion must be 'requested' (is only issued on demand), unless
        autocompletion is set to n (chars inputted after which it starts). Normal
        bindings are F1 Shift_Enter, Control_Enter or right-click and will 
        fill the gtk.EntryCompletion associated to the entry with values
        accordingly.

        Bindings are set in SqlText inside text_editing_started_cb
        while in SqlMask inside miniwidgets (actually only VarcharWidget and FKeyWidget)

        widget.connect('button-press-event',self.completion.keypress_event_cb,  self.field_name)

        It requires quite a lot of object be already setup in the master
        (actually SqlMask or SqlTable?)
        self.master.mapper_info.fields: an InspectMapper Object
        self.master.engine
        self.master.mapper
        self.master.values in case of an id, completion will substitute it
             with a description field, for the user benefit. The real value
             of the field will be hold there.
        self.master.gui_fields (mask wdgets): the mapping field_name -> widget
        
        """


        self.master = master
        self._ids = {}
        hid = self.master.connect('delete-event', self.destroy)
        self._ids['master_delete_event'] = (master, hid)
        self.lookup_values = {}
        self.MATCH_OPERATOR = OP.get(self.master.metadata.bind.name, 'ILIKE')
        self.widget = widget
        self.field_name = field_name
        self.completion = self.prepare_completion()
        self.column = self.master.mapper_info.fields[field_name]['col']
        try:
            self.table = self.column.table
        except AttributeError:
            raise exc.ColumnWithoutTable("Column %s does not have .table attribute" % field_name)
        self.format = get_description(self.table, attr='format')
        self.description = tables[self.table.name].description
        self._attrs = tables[self.table.name].attrs
#        self.columns = [self.master.mapper_info.fields[field_name]['col'] for field_name in self.attrs]
        self.columns = [self.master.mapper_info.fields[self.field_name]['col']]
#        self.attrs = tables[self.table.name].attrs
        self._group_by = None
        self._order_by = [self.column]
        self._dynamic_filters = None
        self.mapper = self.master.mapper # used to track path relationship
        self.force_enum = False
        self.displaying_completion = False
#        self.query = self.master.session.query(getattr(self.master.mapper.class_, self.field_name)).autoflush(False)
        self.query = self.master.session.query(*self.columns).autoflush(False)
        self.filtered_query = None
        self.match_dict = {}
        
    def destroy(self, sqlwidget):

        for obj, hid in self._ids.values():
            obj.disconnect(hid)
        del self._ids

        for attr in ('master', 'query', 'mapper', 'filtered_query', 'widget',):
            try:
                delattr(self, attr)
            except AttributeError, e:
                pass
        
    def set_group_by(self, field_name):
        """
        Modify the way output is presented adding a group field.
        If group_by is not already in table.attrs, add it runtime

        :param field_name: the field name
        """
        if not field_name in self.attrs:
            self.attrs += [field_name]
            group_column = self.table.columns[field_name]
            self.columns += [group_column]
            if hasattr(self.query, 'add_columns'):
                self.query = self.query.add_columns(group_column)  # SqlAlchemy 0.6
            else:
                self.query = self.query.add_column(group_column)   # SqlAlchemy 0.5
            if self.filtered_query:
                self.filtered_query = self.filtered_query.add_columns(grup_column)

        self._group_by = field_name
        self._order_by = [self.table.columns[f] for f in [field_name, self.description]]
        
    def get_group_by(self):

        return self._group_by

    def get_entry(self):
        return self.widget.get_entry()

    group_by = property(get_group_by, set_group_by)
    entry    = property(get_entry)

    def _get_attrs(self):
        return self._attrs
    
    def _set_attrs(self, attrs):
        self._attrs = attrs
        self.columns = [getattr(self.mapper.class_, field_name) for field_name in attrs]
        self.query = self.master.session.query(*self.columns).autoflush(False)
        
    attrs = property(_get_attrs, _set_attrs)

    def prepare_completion(self):
        """
        Prepare an EntryCompletion suitable for... sqlcompletion
        """

        completion = gtk.EntryCompletion()
        completion.set_property('popup-set-width', False)
        completion.set_property('minimum-key-length', 0)
#        completion.set_property('popup-single-match', False)   ???
        completion.connect('match-selected', self.match_selected_cb, self.field_name)
        renderer = gtk.CellRendererText()
        completion.pack_start(renderer)

        completion.add_attribute(renderer, 'markup', self.MARKUP_COL)

        ## we match against the description field
        ## from the reference docs:
        # The match function is used by the entry completion to determine
        # if a row of the associated tree model should be in the completion list
        completion.set_match_func(self.match_func)
        self.model = self.prepare_model()
        completion.set_model(self.model)
        
        return completion

    def prepare_model(self):
        return gtk.ListStore(str, object, bool)
    
    def add_completion(self, entry):
        """ add a completionEntry to an Entry
        """
        entry.set_completion(self.completion)

    def add_callbacks(self, entry):
        entry.connect('button-press-event', self.pop_menu,  self.field_name, 3)
        entry.connect('key-press-event', self.keypress_event_cb,  self.field_name)
        entry.connect('key-release-event', self.keypress_event_cb,  self.field_name, 'release')

        
### Filling & popping the completion
    def show_possible_completion(self, widget, mode, apply_filter=True, pop=True, sb=True,
                                 value=None, return_sql=False, one=False):
        """
        fill in a ListStore to use with completion, fetch data from db
        
        :param mode: determines the match of the already typed text:

           :start: only matching data starting with typed text
           :regexp: typed text is a regexp (*~ or ILIKE)
           :enum: all values
           :exact: triggers the completion machanism but just for the exact match

        :param apply_filter: filter added with .filter() will be applied
        :param return_sql:   boolean only the sql is returned (debug purpose)
        :param value:        value to use as "displayed value". debug purpose
        :param pop:          don't try to pop the selection (debug purpose)
        :param one:          return the result that should be just one (used internally
                             within check_existance)
        """
        self._apply_filter = apply_filter
        if self.force_enum:
            mode = 'enum'
        self.mode = mode
        if sb:
            # TIP: status bar 
            self.master.sb(_("search mode: %s") % mode)
        self.model.clear()
        self._prev_group_by_value = None

        result = self.select_values(mode, return_sql=return_sql, value=value)
        self._needs_recalculating = True
        if return_sql:
            return debug_inline_params(result, bind=None)

        self.completion.set_model(None)
        if not result:
            if not hasattr(self, 'column_lookup'):
                # Nothing to do if it's not a foreign key
                return
            try:
                f = self.master.gui_fields[self.field_name]
                q = self.filtered_query or self.query
                result = q.filter_by(**{self.column_lookup.name : f.get_value()})
            except exc.ValidationError:
                # ValidationError occurs when f.get_value() fails finding a possible completion
                return

        for obj in result:
            self.append_to_model(obj)
        self.completion.set_model(self.model)

        if one and mode == 'exact':
            ## 'exact' is used by self.check_existance just one result will
            ## be returned even if no check is done that more that one exists

            ## 'obj' may not be defined here. It happens when 1. you have a
            ## filter on completion, 2. you bypass it with Control-Alt,
            ## 3. select a match that activates the cell correctly. A second
            ## pass on the same cell, if you try to complete, exact will be
            ## used an will fail.
            
            try:
                return DictLike(obj)
            except UnboundLocalError:
                return

        if pop:
            self.make_completion_to_pop(self.get_entry())
        else: # doctest purpose
            for row in self.model:
                print self.model.get_value(row.iter, 1)

    def debug_completion_sql(self, mode='start', value='', apply_filter=True):
        """
        Debug version of show_possible_completion
        """
        return self.show_possible_completion(None, mode, return_sql=True, value=value,
                                             apply_filter=apply_filter)
    
    def match_func(self, completion, key, iter):
        """
        When editing, this function limits the visible entry of the model
        """
        ## I want to have also group_by field in the completion, but only when
        ## thare's a match to be shown under that group
        ## so I need to passs twice, this is done just once each completion
        ## popup
        text = self.model.get_value(iter, self.SEARCH_COL)
        prev = getattr(self, '_prev_match_value', None)
        
        if self.mode == 'enum':
            return True

        if key != prev or self._needs_recalculating:
            self.match_dict = {}
            self._prev_match_value = key
            ## recalculate if the text (key) in the entry was changed
            self.model_set_match_col(key, )
            self._needs_recalculating = False

        return self.match_dict.get(self.model.get_path(iter), False)


    def model_set_match_col(self, key):
        """
        set MATCH_COL to be returned by match_func in a 2 pass process:
        
        """
        miter_dict = {}
        i = 0
        for row in self.model:
            value = self.model.get_value(row.iter, self.VALUE_COL)
            text  = self.model.get_value(row.iter, self.SEARCH_COL)
            obj   = self.model.get_value(row.iter, self.OBJ_COL)
            descr   = self.model.get_value(row.iter, self.DESCRIPTION_COL)

            path = self.model.get_path(row.iter)
            if value is None:
                ## it's a group_by field
                #self.model.set_value(row.iter, self.MATCH_COL, False)
                # store it's iter but set to false for the moment (will not match)
                miter_dict[descr] = [path, False]

            else:
                match = False
                ## start mode
                try:
                    if not key:
                        match = True
                    elif text is None:
                        match = False
                    elif self.mode == 'start' and re.search("^%s" %(key), text, re.IGNORECASE):
                        match = True
                    elif re.search(key, text, re.IGNORECASE):  # regexp mode
                        match = True
                except re.error, e:
                    match = False
                    
                if match and self._group_by:
                    ## switch ON the display of group by label in completion
                    try:
                        miter_dict[obj[self._group_by]][1] = True
                    except IndexError, e:
                        print "Probable missing value for %s" % text
                    except KeyError:
                        ## FIXME but I have not uderstood why I need it.
                        # I get here when -after accepting a completion- I go back and delete some chars
                        pass
                    
                self.match_dict[path] = match

        for path, val in miter_dict.values():
            self.match_dict[path] = val

    def append_to_model(self, obj):
        """
        How each selected record gets to the model
        """
        m_iter = self.model.append(None)
        if hasattr(self, 'possible_values'):
            value = obj
        else:
            value = markup_escape_text(getattr(obj, self.field_name))
        self.model.set(m_iter,
                       self.VALUE_COL, value,
                       self.MATCH_COL, True)

    def make_completion_to_pop(self, entry):
        """
        Create an event that will cause completion to pop
        """
        self.displaying_completion = True
        entry.grab_focus()
        # entry.emit('changed') ## needed to make completion to pop
        # read note in widget.pop_completion()
        self.widget.pop_completion()
        ## we don't want selection to prevent autocompletion from deleting already written text
        entry.select_region(-1,-1)
        
### Call back
    def match_selected_cb(self, wdg, model, iter, field_name):
        """
        after selecting an entry store the value in self.values and set
        the entry with the correct value.
        """
        # the completion model has 1 or 4 columns (in case of FKey):
        # 0:  the real value to be put in the db
        # 1:  the value to be shown in the field
        # 2:  the value to be shown in the drop down completion menu
        # 3:  the row return by the SELECT when building the completion
        #         if more fields are present more columns get written

        value = model.get(iter, self.VALUE_COL)[0]
        obj = model.get_value(iter, self.OBJ_COL)
        
        self.master.set_value(field_name, value, fkvalue=None, initial=False)
        ## here field.set_value is not yet needed. It's there just in case the field has some
        ## validation logic
        self.master.gui_fields[field_name].set_value(value, initial=False)

        self.displaying_completion = False
        self.master.run_hook('on_completion', obj, field_name=self.field_name)
        return True

### Sql SELECT
    def select_values(self, mode, return_sql=False, value=None):
        """
        execute the SELECT DISTINCT and return values
        """
        oper = self.get_match_operator()

        if hasattr(self, 'possible_values'):
            return self.get_values(mode, value)

        if self._apply_filter:
            query = self.filtered_query or self.query
        else:
            query = self.query

        if not mode == 'enum':
            filtering_value = self.get_displayed_value(value=value)
            self.autostart_last_length = len(str(filtering_value))

            if filtering_value:
                query = self.compose_select_statement(query, oper, filtering_value)
        query = self.add_dynamic_filters(query)

        query = query.order_by(*self._order_by).distinct()
        if return_sql:
            return query
        
        return query.all()

    def get_values(self, mode, value):
        """
        return all completion values when a list was supplied explicitey
        using set_values
        """
        if isinstance(self.possible_values, (list, tuple)):
            if not value or mode == 'enum':
                return self.possible_values
            else:
                if mode == 'regexp':
                    return [v for v in self.possible_values if re.search(value, v)]
                else:
                    return [v for v in self.possible_values if re.match(value, v)]
        else:
            return self.possible_values(value)

    def set_values(self, values):
        """
        Set explicitely the possible completion values.

        :param values: a list of values or a callable that will return a list
                       of possible values

        Can be a list or a callable that will be called to get the
        real list of values passing the (possible) text in the entry
        as parameter
        """
        if not callable(values):
            sorted(values)

        self.possible_values = values
        
    def compose_select_statement(self, query, oper, value):

        if oper:
            if oper == 'ILIKE':
                query = query.filter(self.column.ilike(value))
            else:
                query = query.filter(self.column.op(oper)(value))
            
        return query
    
    def get_displayed_value(self, value=None):

        if value is not None:
            val = value
        else:
            val = self.master.get_value(self.field_name, shown=True) or ''

        self.autostart_last_length = len(str(val))
        if isinstance(val, basestring):
            return self.add_for_LIKE_and_REGEXP(val.strip('\\'))

    def get_match_operator(self):
        
        ## FIXME: pretty stupid at the moment...
        if self.mode == 'start':
            oper = self.MATCH_OPERATOR
        if self.mode == 'regexp':
            oper = self.MATCH_OPERATOR
        if self.mode == 'exact':
            oper = '='
        else:
            oper = self.MATCH_OPERATOR

        return oper

    def add_for_LIKE_and_REGEXP(self, value):
        """add a % simbol to get expansion if completion is attempted in LIKE mode""" 

        if self.MATCH_OPERATOR in ('LIKE', 'ILIKE'):
            if self.mode == 'start':
                if not value.endswith('%'):
                    value += '%'
                
            if self.mode == 'regexp':
                if not value.startswith('%'):
                    value = '%' + value + '%'

        elif self.MATCH_OPERATOR in ('~*',):
            if self.mode == 'start':
                if not value.startswith('^'):
                    value = '^' + value

        return value
    
    def add_dynamic_filters(self, query):
        """
        Add dinamic filters set with ``.filter``
        """
        if not self._dynamic_filters  or not self._apply_filter:
            return query

        ## substitute values
        kw = {}
        OR = self._dynamic_filters[0]
        dynamic_filters = self._dynamic_filters[1:]

        for key, val in dynamic_filters:
            value =  self.parse_value(val)   # get a possible dynamic filter
            if value:
                kw[key] = value
        
        if kw:
            return django2query(query, self.mapper, OR=OR, **kw)
        else:
            return query

### Misc
    def autostart_completion(self):
        """
        Completion starts on demand or:
        1. when more that self.autostart chars have been written
        2. if text in entry has fewer chars than chars that triggered it
        """
        if self.displaying_completion:
            return
        
        if self.autostart:
            text = self.master.get_value(self.field_name, shown=True)
            length = len(text or '')

            if (not self.autostart_last_length  and length >= self.autostart) \
                   or (length + 1 < self.autostart_last_length):
                autostart = self.autostart
                self.autostart = False
                self.show_possible_completion(self.widget.get_entry(), 'regexp')
                self.autostart = autostart
        return True
    
    def pop_menu(self, wdg, ev, field_name, num_button=3):
        """pops a menu with chooices of different completion::
              - regexp
              - start
        """
        from sqlkit.widgets.table.tablewidgets import CellWidget
        from sqlkit.layout.misc import StockMenuItem
        
        if not ev.button == num_button:
            return False

        try:
            self.w['M=popup'].destroy()
        except:
            pass

        
        self.master.widgets['M=popup'] = gtk.Menu()
        menu = self.master.widgets['M=popup']
        ## info on field
        
        item = StockMenuItem(label="info on %s" % field_name.replace('_','__'), stock='gtk-info')
        gtk.MenuItem(label="info on %s" % field_name.replace('_','__'))
        item.connect('activate', self.master.show_field_info, field_name)
        label = _("Show all info on this field, db type & Co.")
        item.set_tooltip_text(label)
        menu.append(item)
        
        ## possible values regexp
        # TIP: menu enty in menu on right click on down arro in fkey completion widget
        item = gtk.MenuItem(label=_("Show possible values: regexp  - Ctrl-Enter"))
        if not isinstance(self.widget, CellWidget):
            item.connect('activate', self.show_possible_completion, 'regexp')
        # TIP: yellow tip to menu entry in down arrow in completion widget
        label = _("Show all values in the db that match your string")
        item.set_tooltip_text(label)
        menu.append(item)

        ## possible values starting
        item = gtk.MenuItem(label=_("Show possible values, starting - Shift-Enter"))
        if not isinstance(self.widget, CellWidget):
            item.connect('activate', self.show_possible_completion, 'start')
        label = _("Show all values in the database starting with your string")
        item.set_tooltip_text(label)
        menu.append(item)

        ## edit table referenced as foreign key
        if self.master.is_fkey(field_name):
            item = StockMenuItem(label=_("Edit the referenced table in 'table' mode"),
                                 stock='gtk-leave-fullscreen')
            item.connect('activate', edit_foreign_key_table, self.master, field_name, 'table')
            label = _("Edit the table from which admitted values are taken in 'table' mode")
            item.set_tooltip_text(label)
            menu.append(item)

        if self.master.is_fkey(field_name):
            item = StockMenuItem(label=_("Edit the referenced table in 'mask' mode"),
                                 stock='gtk-leave-fullscreen')
            item.connect('activate', edit_foreign_key_table, self.master, field_name, 'mask')
            label = _("Edit the table from which admitted values are taken in 'mask' mode")
            item.set_tooltip_text(label)
            menu.append(item)

        menu.show_all()
        menu.popup(None, None, None, ev.button, ev.time)
        
        return True
    def keypress_event_cb(self, wdg, event, data=None, when='before'):
        """trigger various callback to keypress
        Set in miniwidgets or in text_editing_started_cb
        A callback connected with connect_after should set when to after
        """
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
        #dbg.write('ksym', ksym, 'mods', mods)
        
        if when == 'release':
            self.autostart_completion()
            return
        if ksym in dir(self):
            return getattr(self, ksym)(wdg, event, data)
        return False

    def key_entry_F1(self, wdg, event, data):
        self.show_possible_completion(wdg, mode='regexp')
        return False
    
    def key_entry_shift_Return(self, wdg, event, data):
        self.show_possible_completion(wdg, mode='start')
        return True
        
    def key_entry_shift_alt_Return(self, wdg, event, data):
        self.show_possible_completion(wdg, mode='start', apply_filter=False)
        return True
        
    def key_entry_ctrl_Return(self, wdg, event, data):
        self.show_possible_completion(wdg, mode='regexp')
        return True
        
    def key_entry_ctrl_alt_Return(self, wdg, event, data):
        self.show_possible_completion(wdg, mode='regexp', apply_filter=False)
        return True
        
    def key_entry_ctrl_alt_f(self, wdg, event, data):
        self.master.filter_panel.short_filter(self.field_name, self.master.relationship_path)
        return True
        
    def key_entry_ctrl_shift_Return(self, wdg, event, data):
        self.show_possible_completion(wdg, mode='enum')
        return True
        
    def key_entry_ctrl_shift_alt_Return(self, wdg, event, data):
        self.show_possible_completion(wdg, mode='enum', apply_filter=False)
        return True
        
    def key_entry_Return(self, wdg, event, data):
        #
        return not self.check_existance(wdg)

    def key_entry_Tab(self, wdg, event, data):
        # waiting for a complete handling of validation
        return False
        check = self.check_existance(wdg)
        return check

    def check_existance(self, entry):
        """
        don't accept false fkey...
        Return True if field exists or validates
        """
        text = entry.get_text()
        
        if not text:
            return True

        if self.master.is_fkey(self.field_name) or (
            self.master.relationship_mode == 'm2m' and not self.master.m2m_editable):
            ## check if the text entered was in fact a complete and legal fkey
            ## or unique field (for m2m)
            if self.master.fkey_is_valid(self.field_name):
                ## see note below on 'on_completion'
                obj = self.show_possible_completion(None, 'exact', one=True)
                self.master.run_hook('on_completion', obj, field_name=self.field_name)
                return True
            try:
                if self.master.is_fkey(self.field_name):
                    clean_value = self.master.gui_fields[self.field_name].clean_value(text, input_is_fkey=False)
                    if clean_value == None:
                        raise exc.NoResultFound

                    self.master.sb(_("Good match"), seconds=4)
                    self.master.set_value(self.field_name, clean_value, fkvalue=text)
                    ## since on_completion needs an obj that must have all attributes defined in
                    ## self.attrs we trigger the complete tour
                    obj = self.show_possible_completion(None, 'exact', one=True)
                    self.master.run_hook('on_completion', obj, field_name=self.field_name)
                    return True

                else:
                    self.master.sb(_("No exact match, trying regexp completion"), seconds=4)
                    self.show_possible_completion(entry, mode='regexp', sb=False)
                    self.master.cell_entry.valid = False
                    return False
                    
            except (exc.NoResultFound, exc.MultipleResultsFound), e:
                self.master.sb(_("No exact match, trying regexp completion"), seconds=4)
                self.show_possible_completion(entry, mode='regexp', sb=False)
                return False
        return True

    def get_obj_no_flush(self, value):
        """
        check if the object exists and .one(), but don't trigger .flush()
        """
        filter_cnd = {str(self.field_name) : value}
        query = self.master.session.query(table2mapper(self.table)).autoflush(False)
        return query.filter_by( **filter_cnd ).one()
        
    def filter(self, OR=False, main_query=False, **kwargs):
        """
        :param main_query: add the filter to the main query
        
        Add filters to the completion. Filters must be expressed in django-like syntax
        Value can be in the form ``$field_name`` (see below)::

          t = SqlMask(...)
          t.completions.field1.filter(cod='$field2')

        would request

           1. to retrieve the value of field2 via t.get_value(field2)
           2. to add .filter(field2 = value) to the query that retrieves the possible
              completions

        Filter conditions are relative *to the mapper of the completion*: for a completion
        on a ForeignKey it's the referenced table's mapper. To state it again and referring
        to example 40 of the demo: if you edit movie table and complete on diector_id, the
        following code would select the ``nation`` of the director in table ``director``::

          t.completions.director_id.filter(nation='IT')

        In point 1. above ``t.get_value()`` is relative to
        the SqlWidget in which the completion is requested.  This is relevant
        when related tables are present in the mask. Field value of the main
        mask can be referred to as ``$main.field_name``

          1. each token starting with ``$`` as in ``$title`` is stripped
             from the ``$`` and the remaining part is used as field_name and
             t.get_value(field_name) is used instead

          2. if the field_name part starts with ``main.`` (as in ``$main.title``)
             t.get_value(field_name) is not issued in the active SqlWidget but in
             the SqlWidget pointed to by ``relationship_leader``

             This in general is the main SqlMask holding possibly different m2m
             tables. This makes it possible for rows in an m2m table to complete
             only with values related to the referring header.
             
        """

        kw_dyn_list = [OR]
        keys = []

        # firstly parse the args for 'dynamic' args ($)
        for key, val in kwargs.iteritems():
            if isinstance(val, basestring) and val.startswith('$'):
                keys += [key]
                kw_dyn_list += [(key, re.sub('^\$', '', val))]
                
        for key in keys:
            kwargs.pop(key)

        # now 'static' filters
        if kwargs:
            if main_query:
                self.query = django2query(self.query, self.mapper, OR=OR, **kwargs)
            else:
                self.filtered_query = django2query(self.filtered_query or self.query,
                                                   self.mapper, OR=OR, **kwargs)

        self._dynamic_filters = kw_dyn_list
        
    def parse_value(self, value):
        """
        return value after 2 substitutions as described in .filter()

        """
        if isinstance(value, str):
            
            if value.startswith('main.'):
                value = value.replace('main.','')
                value = self.master.relationship_leader.get_value(value)
            else:
                value = self.master.get_value(value)
        return value
        

    def __str__(self):
        return "<SimpleCompletion: %s>" % self.field_name
        
class FkeyCompletion(SimpleCompletion):
    """
    A completion that follows foreign key to get values to complete and to substitute for lookup.
    Inherits from :class:`SimpleCompletion`
    """
    VALUE_COL = 0
    DESCRIPTION_COL = 1
    MARKUP_COL = 2
    OBJ_COL = 3
    MATCH_COL = 4
    SEARCH_COL = 5
        
    def __init__(self, master, widget, *args, **kw):
        SimpleCompletion.__init__(self, master, widget, *args, **kw)
        self.table, self.column = get_foreign_info(self.master, self.field_name, names=False)
        self.table_lookup, self.column_lookup = self.table, self.column
        self.description = get_description(self.table, attr='description')
        self.search_field = self.description
        self._attrs = get_description(self.table, attr='attrs', metadata=self.master.metadata)
        if self.search_field not in self._attrs:
            self._attrs += [self.search_field]
        self.format    = get_description(self.table, attr='format', metadata=self.master.metadata)
        self._order_by = [self.table_lookup.c[self.description]]
        self.widget = widget
        class_ = utils.get_class(self.table_lookup)
        if class_:
            self.mapper = class_mapper(class_)
        else:
            class Tbl(object): pass
            self.mapper = mapper(Tbl, self.table_lookup)
        self.columns = [getattr(self.mapper.class_, field_name) for field_name in self.attrs]
        self.query = self.master.session.query(*self.columns).autoflush(False)

    def get_entry(self):
        return self.widget.entry

    def prepare_model(self):
        ## last col is for markup
        return gtk.ListStore(object, str, str, object, bool, str)
            
    def compose_select_statement(self, query, oper, value):

        if oper:
            lookup_col = self.table_lookup.columns[self.search_field]
            if oper == 'ILIKE':
                query = query.filter(lookup_col.ilike(value))
            else:
                query = query.filter(lookup_col.op(oper)(value))
        return query
    
    def match_selected_cb(self, wdg, model, iter, field_name):
        """
        after selecting an entry store the value in self.values and set
        the entry with the correct value.
        """
        # the completion model has 1 or 4 columns (in case of FKey):
        # 0:  the real value to be put in the db
        # 1:  the value to be shown in the field
        # 2:  the value to be shown in the drop down completion menu
        # 3:  the row return by the SELECT when building the completion
        #         if more fields are present more columns get written

        value = model.get(iter, self.VALUE_COL)[0]
        obj = model.get_value(iter, self.OBJ_COL)
        
        fkvalue = model.get(iter, self.DESCRIPTION_COL)[0]

        self.master.set_value(field_name, value, fkvalue=fkvalue, initial=False)

        ## here set_field IS needed. Read the note in fields.FKeyField.set_value
        self.master.gui_fields[field_name].set_value(value, initial=False)

        ## just handier to accept it already
        if not self.master.is_mask():
            self.master.cell_entry.entry.emit('activate')

        self.displaying_completion = False
        self.master.run_hook('on_completion', obj, field_name=self.field_name)
        return True

### What to show
    def append_to_model(self, obj):
        """
        add to the model that has 6 cols
        """
        obj_list = []

        ## FIXME what if we have a multiple pkey?
        fvalue  = getattr(obj, self.attrs[0])
#        fdescr  = getattr(obj, self.description)
        fsearch = getattr(obj, self.search_field)
        
        Obj = DictLike(obj)
        description = unicode((self.format % Obj)).strip()
        m_iter = self.get_iter(obj)
        ## FIXME: what if the pkey is composed?
        self.model.set(m_iter,
                       self.VALUE_COL,       fvalue,
                       self.DESCRIPTION_COL, description,
                       self.MARKUP_COL,      "   %s" % markup_escape_text(description),
                       self.OBJ_COL,         Obj,
                       self.MATCH_COL,       True,
                       self.SEARCH_COL,      fsearch,
                       )

    def get_iter(self, obj):
        # based on self.__prev_group_by_value
        #          self.__prev_group_by_iter

        if not self._group_by:
            return self.model.append(None)
        else:
            prev = getattr(self, '_prev_group_by_value', None)
            new_value = getattr(obj, self._group_by)

            self._prev_group_by_value = new_value
            ## the row is NOT a ??
            if new_value is not None and  new_value == prev:
                return self.model.append(self._prev_group_by_iter)

            else:
                ## add to completion's model
                m_iter = self.model.append(None)
                self._prev_group_by_iter = None
                self.model.set(m_iter,
                               self.DESCRIPTION_COL, new_value,
                               self.MARKUP_COL,   "<b><i>%s</i></b>" % markup_escape_text(new_value),
                               self.MATCH_COL,       True,
                               )
                m_iter = self.model.append(None)
            return m_iter
                    
            
    def get_obj_no_flush(self, value):
        """
        check if the object exists and .one(), but don't trigger .flush()
        """
        
        filter_cnd = {str(self.description) : value}
        query = self.master.session.query(table2mapper(self.table)).autoflush(False)
        return query.filter_by( **filter_cnd ).one()
        
#     def compose_binary_expression(self, **kwargs):
#         return compose_binary_expression(self.table, **kwargs)


    def get_filtered_clause_list(self, **kw):
        """
        apply filter rules to this particular completion request.
        Note: mapper is not available in the general situation, so we
        use table to build the clause. That means we cannot follow any
        further relationship.
        """
        
        clause_list, path = django2sqlalchemy(table=self.table, **kw)
        return clause_list

    def __str__(self):
        return "<FkeyCompletion: %s>" % self.field_name
        
class EnumCompletion(SimpleCompletion):
    """
    A completion that shows enum alternatives.
    Inherits from :class:`SimpleCompletion`
    """
    VALUE_COL = 0
    DESCRIPTION_COL = 1
    SEARCH_COL = 1
    MARKUP_COL = 1
        
    def __init__(self, master, widget, *args, **kw):
        SimpleCompletion.__init__(self, master, widget, *args, **kw)
        self.widget = widget
        self._needs_recalculating = False
    def get_entry(self):
        return self.widget.entry

    def prepare_model(self):
        ## last col is for markup
        return gtk.ListStore(object, str, )
            
    def match_selected_cb(self, wdg, model, iter, field_name):
        """
        after selecting an entry store the value in self.values and set
        the entry with the correct value.
        """
        # the completion model has 1 or 4 columns (in case of FKey):
        # 0:  the real value to be put in the db
        # 1:  the value to be shown in the field
        # 2:  the value to be shown in the drop down completion menu
        # 3:  the row return by the SELECT when building the completion
        #         if more fields are present more columns get written

        value = model.get(iter, self.VALUE_COL)[0]
        
        fkvalue = model.get(iter, self.DESCRIPTION_COL)[0]

        self.master.set_value(field_name, value, fkvalue=fkvalue, initial=False)

        ## just handier to accept it already
        if not self.master.is_mask():
            self.master.cell_entry.entry.emit('activate')

        self.displaying_completion = False
        #self.master.run_hook('on_completion', obj, field_name=self.field_name)
        return True

### What to show
    def show_possible_completion(self, widget, mode, apply_filter=True, pop=True, sb=True,
                                 value=None, return_sql=False, one=False):
        """
        fill in a ListStore to use with completion, fetch data from db
        
        :param mode: determines the match of the already typed text:

           :start: only matching data starting with typed text
           :regexp: typed text is a regexp (*~ or ILIKE)
           :enum: all values
           :exact: triggers the completion machanism but just for the exact match

        :param apply_filter: filter added with .filter() will be applied
        :param return_sql:   boolean only the sql is returned (debug purpose)
        :param value:        value to use as "displayed value". debug purpose
        :param pop:          don't try to pop the selection (debug purpose)
        :param one:          return the result that should be just one (used internally
                             within check_existance)
        """
        self._apply_filter = apply_filter
        if self.force_enum:
            mode = 'enum'
        self.mode = mode
        if sb:
            # TIP: status bar 
            self.master.sb(_("search mode: %s") % mode)
        self.model.clear()

        self.completion.set_model(None)
        field = self.master.gui_fields[self.field_name]

        for idx, text in field.values.iteritems():
            self.append_to_model(idx, text)
        self.completion.set_model(self.model)

        if one and mode == 'exact':  # used by self.check_existance
        ## just one result will be returned even if no check is done that more that one exists
            # I'm not sure that obj is *always* defined!... I believe so!
            return DictLike(obj)

        if pop:
            self.make_completion_to_pop(self.get_entry())
        else: # doctest purpose
            for row in self.model:
                print self.model.get_value(row.iter, 1)
    def append_to_model(self, idx, text):
        """
        add to the model that has 6 cols
        """
        miter = self.model.append(None)
        self.model.set(miter,
                       self.VALUE_COL,       idx,
                       self.DESCRIPTION_COL, text,
                       )

    def get_obj_no_flush(self, value):
        """
        check if the object exists and .one(), but don't trigger .flush()
        """
        
        filter_cnd = {str(self.description) : value}
        query = self.master.session.query(table2mapper(self.table)).autoflush(False)
        return query.filter_by( **filter_cnd ).one()
        
#     def compose_binary_expression(self, **kwargs):
#         return compose_binary_expression(self.table, **kwargs)


    def get_filtered_clause_list(self, **kw):
        """
        apply filter rules to this particular completion request.
        Note: mapper is not available in the general situation, so we
        use table to build the clause. That means we cannot follow any
        further relationship.
        """
        
        clause_list, path = django2sqlalchemy(table=self.table, **kw)
        return clause_list

    def __str__(self):
        return "<FkeyCompletion: %s>" % self.field_name
        
class M2mCompletion(FkeyCompletion):
    """
    A completion that completes on the whole line: each field can be used to choose the same
    record. It's not possible in this mode to compose a new record field by field.

    The lookup of foreign key values needs a different table than the one used to complete.
    This is called table_lookup/column_lookup.

    Inherits from :class:`FkeyCompletion`

    """
    
    VALUE_COL = 0
    DESCRIPTION_COL = 1
    MARKUP_COL = 2
    OBJ_COL = 3
    MATCH_COL = 4
    SEARCH_COL = 5
        
    def __init__(self, *args, **kw):

        SimpleCompletion.__init__(self, *args, **kw)

        self.query = self.master.session.query(self.master.mapper.class_).autoflush(False)

        if self.master.is_fkey(self.field_name):
            table_lookup_real, column_lookup = get_foreign_info(self.master, self.field_name, names=False)
            self.table_lookup = table_lookup_real.alias()
            self.column_lookup = self.table_lookup.c[column_lookup.name]
            self.search_field = get_description(table_lookup_real.name, attr='description',
                                               metadata=self.master.metadata)
            self.sql_join = (self.column == self.column_lookup)
        else:
            self.table_lookup, self.column_lookup = self.table, self.column
            self.search_field = self.column.name
            self.description = self.search_field
        self._order_by = [self.table.c[self.description]]

        self.attrs = copy(get_description(self.table, attr='attrs', metadata=self.master.metadata))
        self.columns = [getattr(self.master.mapper.class_, field_name) for field_name in self.attrs]
        self.search_column = self.table_lookup.c[self.search_field]
        self.columns += [self.search_column]
        
        self.query = self.master.session.query(*self.columns).autoflush(False)
        
        if self.master.is_fkey(self.field_name):
            self.query = self.query.join((self.table_lookup, self.sql_join)).reset_joinpoint()

        
    def match_selected_cb(self, wdg, model, iter, field_name):
        """
        after selecting an entry store the value in self.values and set
        the entry with the correct value.
        """

        value = model.get(iter, self.VALUE_COL)[0]
        obj = model.get_value(iter, self.OBJ_COL)

        if self.master.is_fkey(field_name):
            fkvalue = model.get(iter, self.DESCRIPTION_COL)[0]
        else:
            fkvalue = None
        ## when the Table is used to render a m2m field
        ## we don't want to "create" a new match, just pick an old one
        ## and use that one
            
        try:
            self.master.set_current(pk=value)
        except Exception, e:
            print 'match selected debug', e
            pass

        self.displaying_completion = False
        self.master.run_hook('on_completion', obj, field_name=self.field_name)
        return True
        
    def filter(self, **kwargs):
        """
        """
        # Filtering on an m2m acts on the resulting row, not on single column
        # so we need to have the same filter on all columns

        for completion in self.master.completions:
            completion._filter_single(**kwargs)

    def _filter_single(self, **kwargs):
        FkeyCompletion.filter(self, **kwargs)
        
    def __str__(self):
        return "<M2mCompletion: %s>" % self.field_name
        

### Functions
def debug_liststore(listore):
    j = 0
    for l in listore:
        iter = listore.get_iter_from_string(str(j))
        print listore.get(iter,0), listore.get(iter,1), listore.get(iter,3)
        j += 1

def edit_foreign_key_table(wdg, master, field_name, mode):
    """open a SqlMask to edit the table referenced by this ForeignKey"""
    ## FIXME  - works only with dbproxy

    from sqlkit.widgets import SqlMask, SqlTable
    
    ftable, fkey = get_foreign_info(master, field_name)
    if mode == 'mask':
        m = SqlMask(ftable, dbproxy=master.dbproxy)
        try:
            fkvalue = master.get_value(field_name, shown=False)
            m.set_records(pk=fkvalue)
        except exc.ValidationError, e:
            pass
    else:
        SqlTable(ftable, dbproxy=master.dbproxy)
    
def get_foreign_info(master, field_name, names=True):

    from sqlkit.db.minspect import get_foreign_info

    foreign_keys = master.mapper_info.fields[field_name]['fkey']
    return get_foreign_info(foreign_keys, names=names)


