# Copyright (C) 2005--2010, Sandro Dentella <sandro@e-den.it>
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

.. _filter_panel:

================
FilterPanel
================

The filter panel is the panel where all filter conditions can be written
(remeber that constraints are different in the sense that are filters
applied w/o possibility to remove them). It opens as a window separate from
the main window so that it's easy to hide or keep it at hand.

Each sqlwidget has a FilterPanel even if it doesn't show it

.. autoclass:: FilterPanel
   :members: hide, show, get_tools, reload, set_page, tree, replace_column,
             add_column, clear, short_filter
.. autoclass:: FilterTool
   :members: set_value, get_value, set_operator, get_operator, destroy

When the filter is used from a SqlTable, the output is displayed directly
into the SqlTable.  When the filter is used from a SqlMask the output is
shown in a special tab of the FilterPanel that is really a :ref:`View
<views>` on the output that can be customized to a good degree. Default
representation is ``str(obj)`` unless a you have defined a ``format``
in the :ref:`database attribute description <sqlkit_table>` for that table.

Customizing the output tab
==========================

The default representation of records is a :ref:`View <views>` with a single
column named ``__obj__`` that is a field that creates a str(obj) as
explained above.

If you want to change that representation you just need to substitute the
column in the treeview::

  from sqlkit.import fields
  from sqlkit.db.utils import DictLike

  class CountMovies(fields.IntegerField):
      '''
      A field that counts the movies
      '''
      def clean_value(self, value):
          ## missing a field_name attribute on obj the objct itselt is passed
          return len(value.movies)

  my_mask.filter_panel.replace_column(CountMovies)

Alternatively you can :ref:`add a column <add_view_column>` to the output view
after creating the field and the column you would add it to the view as follows::

    count = CountMovies('n_movies')
    col = columns.VarcharColumn(t, 'n_movies', 'Movie Count', field=count)
    my_mask.filter_panel.view.add_column(col)

At this point you can sort the output on each column and even get totals in it.
  
"""
import re
import gtk
import warnings
from datetime import *

import gobject
import sqlalchemy
from sqlalchemy.sql import select, Join, or_
from babel import dates

from sqlkit import debug as dbg, _, exc, fields
from sqlkit.db import minspect
from sqlkit.db.utils import tables, get_description, DictLike
from sqlkit.db.django_syntax import django2components
from sqlkit.misc import datetools, utils
from sqlkit.layout import layout, misc
from sqlkit.widgets.table import columns, modelproxy
import completion

FILTER_MENU = '''
<menubar name="FilterMain">
   <menu action="FilterMenu">
     <menuitem action="GoFilter" />
     <menuitem action="GoOutput" />
     <separator name="sep"/>
     <menuitem action="Reload" />
     <separator name="sep2"/>
     <menuitem action="Close" />
  </menu>
</menubar>
'''
OP_MSGID = {
    'REGEXP' : _('Match as regexp'),
    'match' : _('Match as LIKE, "%" automatically added'),
    'ICONTAINS' : _('Match as LIKE case insensitive, "%" automatically added'),
    '~' : _('Match as regexp'),
    '~*' : _('Match as regexp, case insensitive'),
    '!~' : _('Negation of match as regexp'),
    '!~*' : _('Negation of match case insensitive'),
    '=' : _('Equal'),
    '!=' : _('Not equal'),
    '>' : _('Greater than (after than)'),
    '>=' : _('Greater or equal'),
    '<' : _('Less than (before then)'),
    '<=' : _('Less than or equal'),
    'LIKE' : _('LIKE: a "%" means any char - case sensitive'),
    'NOT LIKE' : _('Negation of LIKE'),
    'ILIKE' : _('As LIKE but case insensitive'),
    'NOT ILIKE' : _('Negation of ILIKE'),
    'IS TRUE' : _('The boolean is True'),
    'IS FALSE' : _('The boolean is False'),
    'IS NOT TRUE' : _('The boolean is not True'),
    'IS NOT FALSE' : _('The boolean is not False'),
    'IS NULL' : _('The value is not set'),
    'IS NOT NULL' : _('The value is set'),
    'ID' : _("ID equality (don't follow foreign table)"),
    'EMPTY OR NULL' : _("The value is NULL or empty"),
#    '' : _(''),
    }


class FilterPanel(object):
    """A panel that manages filter conditions of a query: number of records,
    field names and output to point & click in case of a panel of a SqlMask

    """

    tree = None
    """The name of an attribute that will work as grouping attribute.
    The output TreeView will show records grouped by the same attribute as parent/child.
    It should be improved as the parent is a the record and not a row with the only
    grouping attribute.
    """

    def __init__(self, master, visible=True):
        
        """constructor need to know who is the 'master' ie the widget (a mask
        or a table instance) that will display the result. 

        The filter for a SqlMask has a TreeView to show the results and to easy
        browse them.

        """
        self.master = master
        self._ids = {}
        self.dont_record_display = False
        handler_id = self.master.connect('delete-event', self.destroy)
        self._ids['master_delete_event'] = (master, handler_id)
        self.get_layout(visible=visible)
        self.row = 0  # counter for position of fields
        self.default_reload = True
        
        self.search_filter_widgets = []         ## list of FilterTools instances
        self.search_filter_field_names = []     ## field_names used
        self.bind_name = self.master.metadata.bind.name
        self.tree = False
        self._last_focused_entry = None
        if master.is_mask():
            self._id_record_selected = master.connect('record-selected', self.record_selected_cb)
            h1 = self.master.connect('record-deleted', self.record_deleted_cb)
            h2 = self.master.connect('record-new', self.record_added_cb)
            self._ids['master_record_selected'] = (master, self._id_record_selected)
            self._ids['master_record_deleted'] = (master, h1)
            self._ids['master_record_new'] = (master, h2)
        self.prepare_actions()

    def record_selected_cb(self, mask):
        """
        callback on record selection
        """
        self.select_output_path(obj=mask.current, block=True)
        
    def record_deleted_cb(self, mask, obj):
        """
        callback on record deletion
        """
        path = self.get_path_for_obj(obj)
        if path is not None:
            self.model.remove(self.model.get_iter(path) )
        
    def record_added_cb(self, mask):
        """
        callback on record deletion
        """
        try:
            self.model.append([mask.current])
        except:
            ## FIXME: I should consider also  
            self.model.append(None, [mask.current])
        
    def get_layout(self, visible=True):
        """create the filter panel widget"""
        if self.master.is_mask():
            lay = """
            {H.a {V.menu } {O.a tb=gtk-refresh ts=limit tb=gtk-close } }
            {N.0 %filter
               {|T.fld }
               %output
               { TVS=out}
            }
            """
        else:
            lay = """
            {H.a {V.menu } {O.a tb=gtk-refresh ts=limit tb=gtk-close } }
               {|T.fld }

            """
        self.l = layout.Layout(lay, title=_('Filter Panel'), opts="s", label_map=self.master.label_map)
        self.l.prop('Window', 'visible', visible)
        self.l.prop('O.a', 'show_arrow', 'FALSE')
        self.l.prop('A=.fld', 'yscale', '0')
        self.l.elements['H.a'].pack_properties['y-options'] = ''
        self.l.prop('O.a', 'toolbar_style', 'GTK_TOOLBAR_ICONS')

        if self.master.is_mask():
            ## TIP: filter page of the filter panel
            self.l.tip('filter', _('Add filters for your query'))
            ## TIP: output page of the filter panel
            self.l.tip('output', _('Result page for your query'))

        self.w = self.l.show(x=self.hide)
#        self.w['s=limit'].set_value(self.master.limit)
        adj = self.w['s=limit'].get_adjustment()
        adj.set_all(self.master.limit, 0, 10000, 10, 100, 0)
        self.l.connect(
            ('tb=gtk-close', 'clicked', self.hide),
            ('tb=gtk-refresh', 'clicked', self.reload_cb)
                        )
        self.w['label-cursor'] = gtk.gdk.Cursor(gtk.gdk.HAND1)
        if 'TV=out' in self.w:
            self._add_treeview()
        if 'N.0' in self.w:
            self.w['N.0'].connect_after('switch-page', self.on_switch_page)

    def _add_treeview(self):

        class ObjField(fields.VarcharField):
            """
            A field that represents the obj for filter_panel
            """
            def clean_value(self, value):
                return str(value)

        field = ObjField('__obj__')
        self.master.gui_fields['__obj__'] = field
        col = columns.VarcharColumn(self.master, '__obj__', _('output'), field=field)
        self.view = self.create_view()
        self.view.add_column(col)
        self.selection = self.view.treeview.get_selection()
        self.selection.connect('changed',self.on_selection_changed)

    def prepare_actions(self):
        self.actiongroup   = gtk.ActionGroup('Filter')

        self.actiongroup.add_actions([
            ('FilterMenu', None, _('Filter actions')),
            ('Reload', gtk.STOCK_REFRESH, _('Reload from db'), '<Control>r', None, self.reload_cb),
            ('Close', gtk.STOCK_CLOSE, _('Close the panel'), '<Control>q', None, self.hide),
            ], )
        self.actiongroup.add_actions([
            ('GoFilter', None, _('Go to filter panel'), '<Control>l', None, self.set_page),], 'filter')
        self.actiongroup.add_actions([
            ('GoOutput', None, _('Go to output panel'), '<Control>o', None, self.set_page),], 'output')
        self.ui_manager = gtk.UIManager()
        self.accel_group = self.ui_manager.get_accel_group()
        self.l.widgets['Window'].add_accel_group(self.accel_group)
        self.ui_manager.insert_action_group(self.actiongroup, 10)
        self.ui_manager.add_ui_from_string(FILTER_MENU)
        
        ## pack menu and toolbar if it's a toplevel
        header = self.l.widgets['V.menu']
        menu    = self.ui_manager.get_widget('/FilterMain')
        header.add(menu)
        #header.add(toolbar)


    def go_to_filter(self, action):
        
        self.set_page('filter')
        
    def replace_column(self, field_class, field_name='__obj__'):
        """
        Replace the column of the output treeview with a customized one

        :param field_class: a subclass of ``sqlwidget.fields.Field``
               with a proper ``clean_value`` method
        :param field_name: the field_name of the column, Default: ``__obj__`` (i.e. the
               name used for the default column of the output treeview

        """
        
        field = field_class(field_name)
        col = columns.VarcharColumn(self.master, '__obj__', _('output'), field=field)
        self.view.treeview.remove_column(self.view.tvcolumns['__obj__'])
        self.view.add_column(col, 0)
        self.master.gui_fields[field_name] = field
        
    def add_column(self, field_name):
        """
        Add a column among already defined fields in gui_fields

        :param field_name: the field_name of the field

        """
        
        self.view.setup_columns([field_name])
        
    def sb(self, message, seconds=None):
        """
        Write messag on the status bar
        """
        self.l.sb(message, seconds=seconds)
        
    def add_filter(self, active=True, force_=True, **kwargs):
        """
        add a filter using django-like syntax

        :param active: make the filter active (default True). This hides the possibility to
            add a filter on a field named ``active``. In this case you can use the longer version
            that is ``active__eq=True``
        :param force_: force the creation of a new widget, even if one is already present
        :param kwargs: any paramenter allowed per syntax of the django_like syntax as explained
            in the :ref:`chapter on constraints <constraints>`
        
        """
        for key, val in kwargs.iteritems():
            path, op, op_str, value, col, join_args = django2components(self.master.mapper, {key: val})
            master = self.get_related_master(self.master, path)
            filter_tool = self.add(None, None, col.name, master, force=force_)
            if not filter_tool: 
                return
            filter_tool.set_active(active)

            if filter_tool.is_filter_value(value):
                filter_tool.set_value(value)
            filter_tool.set_operator(op, value)

    def get_related_master(self, master, path=None):
        """
        Return the SqlTool that manages the data at 'path'.
        E.g.: if the mapper is the one for movie, and the 'path'  is 'genres'
        as in the doc example, ``get_master``  would return the SqlTable that
        manages the collection of records returned by the relation 'genres'
        """

        for elem in path:
            master = master.related[elem]
        return master


    def add(self, wdg, ev, field_name, master, after=None, show=True, force=False, value=None):
        """
        add a FilterTool to the filter panel + operator and string entry
        after: entry will be positioned after widget 'after'
        """
        if not self.master.ui_manager.get_action('/Main/File/Filters').is_sensitive():
            return
        ## FIXME: after and show?
        search_path = "%s__%s" % ("__".join(master.relationship_path), field_name)
        if not search_path in self.search_filter_field_names or force:
            widget = get_filter_widget(field_name, self, master, value)
            widget.search_path = search_path
            self.search_filter_widgets += [ widget]
            self.search_filter_field_names  += [search_path]

        self.set_page(name='filter')

        if show:
            self.w['Window'].show_all()
        self.w['Window'].present()
        try:
            return widget
        except:
            return None

    def set_page(self, action=None, name=None):
        """
        set the tab in the filter. Tab name can be 'filter' or 'output'.
        Sqlmasks only have 'filter'.

        :param name: name of the tab in the filter widget: *filter* or *output*
        """
        if 'N.0' in self.w:
            if name == 'filter':
                self.w['N.0'].set_current_page(0)

            if name == 'output' and self.master.is_mask():
                self.w['N.0'].set_current_page(1)
        
        
    def hide(self, widget=None, event=None):
        """
        Hide the Filterpanel

        :param widget: not neeeded: it' here to allow using it in callback
        :param event: not needed: see above
        """

        self.w['Window'].set_property('visible', False)
        return True  # stops further processing...
    
    def show(self):
        """
        Present the filter panel
        """
        self.w['Window'].present()
        
    def get_tools(self, field_name):
        """
        return a list of FilterTool for *field_name*

        :param field_name: name of the field
        
        """
        return [w for w in self.search_filter_widgets if w.field_name == field_name]

    def destroy(self, window=None):

        for obj, hid in self._ids.values():
            obj.disconnect(hid)
        del self._ids

        if window:
            self.w['Window'].destroy()
        for attr in ('easytv', 'search_filter_widgets', 'l', 'model', 'selection', 'w'):
            try:
                delattr(self, attr)
            except AttributeError, e:
                pass
            
    def entry_focus_cb(self, entry, event=None):

        self._last_focused_entry = entry
        
    def on_switch_page(self, notebook, junk, page_n):

        if page_n == 0 and self._last_focused_entry:
            gobject.idle_add(self._last_focused_entry.grab_focus)
        
    def short_filter(self, field_name, relationship_path=None):
        """Apply a filter getting the value from the table/mask

        This is a shortcut for the longer operation:

          1. add a filter widget
          2. set a value
          3. reload

        it is meant to be called from a connect in a (varchar) widget
        by pressing C-M-f. It will:

          1. add a filter
          2. get the value for the filter from the text widget
          3. set that value in the filter widget
          4. disreguard the value
          5. launch realod
          6. disable the filter so that subsequent searches on different fields
             won't be affected
        """
        ##FIME: possible clash of names between related objects
        if relationship_path:
            master = self.master.related[relationship_path[0]]
            value = master.get_value(field_name)
            key = "%s__%s__icontains" % (master.relationship_path[0], field_name)
        else:
            master = self.master
            value = self.master.get_value(field_name, shown=True)
            key = field_name + "__icontains"
            
        self.add_filter(**{key : value, 'force_' : False})
        tool = self.get_tools(field_name)[0]
        tool.set_value(value)
        tool.set_active(True)
        initial_value = master.gui_fields[field_name].initial_value
        master.set_value(field_name, initial_value)
        self.reload()
        tool.set_active(False)
        
##### reload & TreeView
    def reload(self):
        """issue a reload operation on master. Callback of reload button"""

        length = 0
        if 'TV=out' in self.w:
            display = False
        else:
            display = True
            
        if self.default_reload:
            try:
                length = self.master.reload(limit=self.get_limit(), display=display )
            except (exc.DialogValidationError, exc.ValidationError), e:
                return

        if 'TV=out' in self.w:
            if length:
                self.master.modelproxy.fill_model(clear=True)

                self.set_page(name='output')
                self.select_output_path(0, block=False)
                self.view.treeview.grab_focus()
                self.tv_resize()
                self.view.on_zoom_fit()
            else:
                self.model.clear()

        self.l.sb(_('Total N. of records: %s' % length))

    def select_output_path(self, path=None, obj=None, block=False):
        """
        Select path ``path``. If path is null and obj is not null try finding path at which is obj

        :param block: block record display (when selction is already an answer to record_display)
        """
        if block:
            self.dont_record_display = True
        if path is None and obj:
            path = self.get_path_for_obj(obj)

        if path is not None and len(self.model):
            self.selection.select_path(path)
            self.view.treeview.scroll_to_cell(path)
        self.dont_record_display = False
            
    def get_path_for_obj(self, obj):
        """
        return path for object
        :param obj: the object for which we neeed the path
        """
        path_list = [None]
        def compare(model, path, iter):
            row_obj = model.get_value(iter, 0)
            if row_obj == obj:
                path_list[0] = path
                return True
            return False
        
        self.model.foreach(compare)
        return path_list[0]

    def reload_cb(self, widget):
        """callback from reload button
        """
        self.reload()

    def set_reload(self, mapper=None, join=None, tables=None):
        """A different method to filter & select is provided
        the scenario is that you have many synced sqlwidgets, you want to provide the
        possibility to select a record in a table with different records in other
        tables and be able to select one particular pair of them from the
        filter tree.

        You need to pass a join to issue the select on and a method in
        actions called 'on_filter_reload' to wich is passed only an
        argument: a dictionary with all the attributes of the collected
        record.

        If you pass tables to set_reload, each table is autoloaded and joined
        to the preceding. The returned join is used.
        
        """
        self.default_reload = False

        if tables:
            if isinstance(tables, str):
                T = {}
                tables = re.split('[ ,]+',tables)
                for tbl in tables:
                    T[tbl] = sqlalchemy.Table(
                        tbl, self.master.metadata, autoload=True)

                for tbl in tables[1:]:
                    join = T[tables[0]].join(T[tbl])
                
        if join:
            class Join(object): pass
            mapper = sqlalchemy.mapper(Join, join)

        self.mapper = mapper
        self.map_fields = minspect.InspectMapper(mapper)

    def create_view(self, field_list=None):
        """
        create a sqlkit.widgets.table.column.View to represent the objects
        """
        if not hasattr(self.master, 'views'):
            self.master.views = utils.Container()
        treeview = self.w['TV=out']

        view = columns.View(master=self.master, name='filter_panel', treeview=treeview,
                    field_list=field_list, ro=True)
        self.master.modelproxy = modelproxy.ModelProxy(self.master, treeview=treeview)
        view.treeview.set_model(self.master.modelproxy.modelstore)
        self.master.views['filter_panel'] = view
        return view
    def _get_model(self):
        return self.master.modelproxy.modelstore

    model = property(_get_model)
    
    def tv_resize(self):
        tv = self.w['TV=out']
        tv.realize()
        X, Y, width, height, bit = tv.window.get_geometry()
        if height < 100:
            tv.set_property('height-request', 300)
            
    def on_selection_changed(self, *args):
        # when clicking on the teeview we get 2 args: treeView, event
        # when changing selection we only have 1 arg: gtk.treeSelection
        # when clicking 'Refresh' we get e gtk.TreeSelection but no
        #      iter get selected
        ## first guess: we selected w/ pointer
        if self.dont_record_display:
            return
        model, iter = self.selection.get_selected()

        ## we don't have a selection
        if iter is None:
            try:
                ## we moved along the treeview w/ arrows
                wdg, ev = args
                path = wdg.get_path_at_pos(int(ev.x), int(ev.y))[0]
                iter = model.get_iter(path)
            except (ValueError, TypeError), e:
                ## ValueError: deselecting when clicking 'reload'
                ## TypeError: no data in the treeview
                return
            
        if self.default_reload:
            try:
                idx = self.master.records.index(model.get_value(iter, 0))
            except ValueError:
                return
            self.master.handler_block(self._id_record_selected)
            self.master.record_display(index=idx)
            self.master.handler_unblock(self._id_record_selected)
    
    def clear(self):
        "Destroy all filter widgets matered by this FilterPanel"
        for w in list(self.search_filter_widgets):
            w.destroy()
##### SQL
    def get_limit(self):
        """
        Get limits of the select we are issuing
        """
        self.w['s=limit'].update()
        return  self.w['s=limit'].get_value_as_int()
    
    def add_filter_conditions(self, query):
        """Adds to the query all filter conditions
        """
        
        for tool in self.search_filter_widgets:
            query = tool.add_filter_condition(query)

        return  query


    def sql_dbg(self, bool_conds):
        for c in bool_conds:
            print "DBG: ", c.left, c.operator, c.right
        

class FilterTool(object):
    """
    A tool that handles the the filter and provides a mean to modify the query of the
    master (sqlwidget). With the FilterTool you can programmatically set the filter
    active/inactive, change the operator and the filter values.

    You will normally do all this with the ``.add_filter`` method of sqlwidget, but
    you may occasionally need to fine tune the filter in a second time
    """
    STR_STD_OPERATORS = [ 'LIKE', 'NOT LIKE', 'ILIKE', 'NOT ILIKE']
    NULL_OPERATORS = [ 'IS NULL', 'IS NOT NULL' ]
    STD_OPERATORS = [ '>=','<=', '=', '!=', '>', '<', ] + NULL_OPERATORS

    def __init__(self, field_name, panel, master):

        self.panel = panel
        self.master = master
        self.field_name = field_name
        self.master.connect('delete-event', self.destroy)
        self.db_spec = self.master.mapper_info.fields[field_name]

        ## db_spec['table'] may not be defined if the column correspond to an expression
        
        if self.db_spec['table'] is not None and self.master.relationship_path:
            ## use an alias in case we have another filter to the same table
            self.table = self.db_spec['table'].alias()
        else:
            self.table = self.db_spec['table']

        prop = self.master.mapper.get_property(self.field_name)
        cols = prop.columns
        
        if len(cols) >= 2:
            msg = """I'm not able to understand which column you want here:  field_name '%s' has
            several columns: %s""" % (self.field_name, prop.columns)
            raise NotImplementedError(msg)

        if isinstance(self.master.mapper.local_table, Join):
            ## FIXME: no aliasing in this case
            self.col = cols[0]
        else:
            ## Note: here self.table can be the alias of self.master.mapper_info.field[field_name].table
            if self.table is not None:
                self.col = self.table.c[self.field_name]
            else:
                ## no aliasing here: is any possible to alias a _Label/expression?
                self.col = self.db_spec['col']

        self.bind_name = self.master.metadata.bind.name
        self.widget = FilterWidget(self)

    def destroy(self, window=None):
        "Destroy the FilterToold and related widgets and de-register from FilterPanel"
        try:
            self.panel.search_filter_widgets.pop(
                self.panel.search_filter_widgets.index(self))
            self.panel.search_filter_field_names.pop(
                self.panel.search_filter_field_names.index(self.search_path))
        except AttributeError:
            pass
        self.widget.destroy()
        del self.widget
        
##### handling
    def is_filter_value(self, value):
        """
        return True if this value can be written
        This may be dependant on the FilterTool but for the moment is not.
        """
        ## NOTE!!! value in (False, True) is WRONG as '0 == False' is True
        # and so 0 in (False,) is True!...
        if value is False or value is True:
            return False
        return True
    
    def set_value(self, value):
        """
        set the value of the filter. It can be a string or an object (eg. a date())
        """
        self.widget.set_value(value)

    def get_value(self):
        """
        return the current value of the filter
        """
        
        value = self.widget.get_value() 
        f = self.master.gui_fields[self.field_name]
        return f.clean_value(value)

    def get_row_value(self):
        """
        return the current value of the filter
        """
        
        return self.widget.get_value() 

    def set_active(self, active):
        """make the filter active"""

        self.widget.set_active(active)

    def get_active(self):
        """set the filter inactive"""
        
        return self.widget.get_active()

    def set_operator(self, op, value):
        """
        Set the active operator entry in ComboBox/OptionMenu for operator choice
        :param op: the operator
        :param value: the value of the operator 
        """
        self.widget.set_operator(op, value)

    def get_operator(self):
        """
        return the active operator entry in ComboBox/OptionMenu 
        """
        return self.widget.get_operator()

    def get_suitable_operators(self):
        """return list of operators meaningfull for engine/data type
        """
        return self.STD_OPERATORS

    def string_representation(self, value):
        """
        return a string representation suitable for filter entry
        """
        field = self.master.gui_fields[self.field_name]
        return field.get_human_value(value)
    
    def add_filter_condition(self, query):
        if not self.get_active():
            return query
        
        op_value = self.get_operator()

        query = query.reset_joinpoint()

        if self.master.relationship_path:
            # query = query.join(*self.master.relationship_path)
            if len(self.master.relationship_path) == 1:
                query = query.join( (self.table, self.master.relationship_path[0]))
            else:
                ## NOTE: if relationship_path is longer that 1, the table is
                ## not aliased, i.e.: if you place 2 search conditions to
                ## the same table (e.g. searching on staff and manager of a
                ## project- and both manager and staff are m2m relation to
                ## User) will most surely lead to no result
                query = query.join(*self.master.relationship_path)

        if op_value in ('IS NULL', 'IS NOT NULL', 'EMPTY OR NULL',
                        'IS TRUE', 'IS FALSE', 'IS NOT TRUE', 'IS NOT FALSE'):
            # NULL
            if op_value == 'IS NULL':
                return query.filter(self.col == None)
            elif op_value == 'IS NOT NULL':
                return query.filter(self.col != None)
            elif op_value == 'EMPTY OR NULL':
                return query.filter(or_(self.col == None, self.col == ''))
                

            # True/False
            if op_value == 'IS TRUE':
                return query.filter(self.col == True)
            elif op_value == 'IS FALSE':
                return query.filter(self.col == False)

            if op_value == 'IS NOT TRUE':
                return query.filter(self.col != True)
            elif op_value == 'IS NOT FALSE':
                return query.filter(self.col != False)

        else:
            try:
                value = self.get_value()
            except exc.ValidationError, e:
                msg = _("value '%s' cannot be used for field '%s'") % (
                    self.get_row_value(), self.field_name)
                self.master.sb(msg)
                self.panel.sb(msg)
                raise e
            
            if value not in (None, ''):
                if not re.match('postgres|mysql', self.bind_name) and \
                       op_value in ('ICONTAINS', 'MATCH') and \
                       not isinstance(value, list): ## value is a list in FilterEnum 
                    op_value = 'ILIKE'
                    value = '%' + value + '%'

                query = self._compose_field_whereclause(query, value, op_value)
            return query
        

    def _compose_field_whereclause(self, query, value, op_value):
        """
        return a sql whereclause for field

        """
        
        if op_value == "ILIKE":
            return query.filter(self.col.ilike(value))

        else:
            return query.filter(self.col.op(op_value)(value))

    def add_filter_cb(self, menuitem, event, n ):
        self.panel.add(None, None, self.field_name, self.master, force=True)
        
    def __repr__(self):
        return "<%s - %s>" % (self.__class__.__name__, self.master.get_label(self.field_name))

class FilterStringTool(FilterTool):

    def get_suitable_operators(self ):
        
        STD_OPERATORS = self.STR_STD_OPERATORS + ['EMPTY OR NULL'] + self.STD_OPERATORS

        if self.bind_name.startswith('postgres'):
            return  ['~*', '~', '!~*', '!~' ] + STD_OPERATORS

        elif self.bind_name.startswith('mysql'):
            return [ 'REGEXP' ] + STD_OPERATORS

        else:
            return ['ICONTAINS'] + STD_OPERATORS
        
class FilterBooleanTool(FilterTool):

    def get_suitable_operators(self):
        return [ 'IS TRUE', 'IS FALSE', 'IS NOT TRUE', 'IS NOT FALSE' ] + self.NULL_OPERATORS

class FilterDateTool(FilterTool):


    def _compose_field_whereclause(self, query, value, op_value):
        """
        Implement the mini date algebra to allow for relative dates

        """

        try:
            start, stop = datetools.string2dates(value)
        except datetools.WrongRelativeDateFormat:
            msg = _("value '%s' does not seem a valid date and cannot be transformed into a date" % value)
            self.master.dialog(type='ok', icon='gtk-dialog-error', text=msg)
            raise exc.ParseFilterError

        # If 'stop' is not None it means I have a period (eg.: 'y > M')
        # and I use operators to delimit this
        # period ignoring the operator from the widget
                        
        op_value = self.get_operator()
        if not stop:
            query = query.filter(self.col.op(op_value)(start))
        else:
            ## start
            query = query.filter(self.col.op(">=")(start))
            ## stop
            query = query.filter(self.col.op("<=")(stop))

        return  query

    def get_value(self):
        # no cleaning of value until in _compose_field_whereclause
        return self.widget.get_value() 

    def string_representation(self, value):
        """
        when date algebra is used we don't need to do anything
        """
        if isinstance(value, date): 
            return FilterTool.string_representation(self, value)
        else:
            return value
        
        
class FilterFKeyTool(FilterTool):

    def __init__(self, field_name, panel, master):

        FilterTool.__init__(self, field_name, panel, master)

        foreign_keys = self.master.mapper_info.fields[self.field_name]['fkey']
        self.ftable, self.fcol = minspect.get_foreign_info(foreign_keys, names=False)

    def get_suitable_operators(self):

        if self.bind_name.startswith('postgres'):
            return  ['~*', '~', '!~*', '~*' ] + self.STD_OPERATORS + ['ID']

        elif self.bind_name.startswith('mysql'):
            return ['REGEXP' ] + self.STD_OPERATORS + ['ID']

        else:
            return ['ICONTAINS' ] + self.STD_OPERATORS + ['ID']

    def get_value(self):
        # no need to clean this value
        return self.widget.get_value()
    
    def string_representation(self, value):
        """
        a boolean must be always a string
        """
        return str(value)
    
    def _compose_field_whereclause(self, query, value, op_value):
        """return a sql whereclause for field

        In case field is a fkey, and the destination lookup field is not in
        the mapper, it composes a subselect
        """
        if op_value == 'ID':
            return query.filter(self.col == value)
        fdescr = get_description(self.ftable, attr='description')

        if op_value == "ILIKE":
            ids = select([self.fcol], self.ftable.columns[fdescr].ilike(value))
        else:
            ids = select([self.fcol], self.ftable.columns[fdescr].op(op_value)(value))

        query = query.reset_joinpoint()

        if self.master.relationship_path:
            query = query.join(*self.master.relationship_path)

        return query.filter(self.col.in_(ids))

class FilterEnumTool(FilterTool):

    def __init__(self, field_name, panel, master):

        FilterTool.__init__(self, field_name, panel, master)

    def get_suitable_operators(self):

        return ['~', '!~' ] + ['IS NULL', 'IS NOT NULL', 'ID']

    def get_value(self):

        op_value = self.get_operator()
        
        text = self.widget.get_value()
        if not text or op_value == 'ID':
            return text

        field = self.master.gui_fields[self.field_name]
        return [key for key, val in field.column.info['values']
                  if re.search(text, val, re.IGNORECASE)]
    
    def string_representation(self, value):
        """
        a boolean must be always a string
        """
        return str(value)
    
    def _compose_field_whereclause(self, query, value, op_value):
        """return a sql whereclause for field

        In case field is a fkey, and the destination lookup field is not in
        the mapper, it composes a subselect
        """
        from sqlalchemy.sql import not_
        
        if op_value == 'ID':
            return query.filter(self.col == value)

        elif op_value == '~':
            return query.filter(self.col.in_(value))
        
        elif op_value == '!~':
            return query.filter(not_(self.col.in_(value)))
        
        return query

def get_filter_widget(field_name, panel, master, value=None):
    """
    return an instance of a proper FilterTool according to type
    """

    args = field_name, panel, master
    if master.is_date(field_name) or master.is_datetime(field_name):
        return FilterDateTool(*args)

    elif master.is_fkey(field_name):
        return FilterFKeyTool(*args)

    elif master.is_enum(field_name):
        return FilterEnumTool(*args)
    
    elif master.is_boolean(field_name):
        return FilterBooleanTool(*args)
    
    elif master.is_number(field_name):
        return FilterTool(*args)
    
    else:
        return FilterStringTool(*args)
        


# _('output')  _('filter')


class FilterWidget(object):
    
    def __init__(self, tool):

        ## I'd like *not* to .present the widget for any successive field added
        ## but I have not been able to get focus on the window w/o .present()
        self.tool = tool
        self.label_text = tool.master.get_label(tool.field_name)

        ## labels
        self.field_name_event_box = gtk.EventBox()
        self.field_label           = gtk.Label(self.label_text)
        # TIP: appears in the menu in the filter panel to add a second entry of the same field
        label_str = _("Add a new filter on this field '%s'") % self.label_text.replace('_', '__')
        self.field_name_event_box.set_tooltip_text(label_str)
        self.check_button         = gtk.CheckButton()

        self.check_button.set_active(True)
        #self.tool.panel.l.tooltips.set_tip(self.check_button, _("Use this filter"))
        self.check_button.set_tooltip_text( _("Use this filter"))
        
        self.field_name_event_box.add(self.field_label)
        self.field_label.set_property('xalign', 0)
        self.field_name_event_box.connect('button-press-event', self.tool.add_filter_cb, 1)

        ## combo for operator
        self.operator = self.get_operator_chooser()

        ## get_active_text per riprenderlo...
        ## entry

        self.field_widget = gtk.Entry()
        self.field_widget.connect('focus-in-event', self.tool.panel.entry_focus_cb)
        self.field_widget.connect('activate', self.tool.panel.reload_cb)
        if isinstance(self.tool, FilterDateTool):
            self.field_widget.connect('changed', self.date_changed_cb)

        Tbl = self.tool.panel.w['T.fld']
        r = self.tool.panel.row
        c = 0
        self.widgets = [ self.field_name_event_box, self.operator, self.check_button ]
        ftype  = self.tool.master.get_field_type(self.tool.field_name)
        
        if self.tool.master.is_enum(self.tool.field_name) or not issubclass(ftype, bool):
            self.widgets += [self.field_widget]
            
        for wdg in self.widgets:
            Tbl.attach(wdg, c, c+1, r, r+1, xpadding=4)
            c += 1
        self.tool.panel.row += 1
        Tbl.show_all()
        self.field_widget.grab_focus()

    def get_operator_chooser(self):
        """
        Build the chooser for the operator.
        I used deprecated OptionMenu since ComboBox does not give the opportunity to
        add tooltips
        """

        operators = self.tool.get_suitable_operators()
        warnings.simplefilter('ignore', DeprecationWarning)
        operator = gtk.OptionMenu()
        operator.set_tooltip_text(_('Click here to select an operator'))
        warnings.resetwarnings()

        menu = gtk.Menu()
        operator.set_menu(menu)

        for op in operators:
            entry = gtk.MenuItem(op)
            menu.append(entry)
            entry.set_data('value', op)
            entry.set_tooltip_text(OP_MSGID[op])
        operator.set_history(0)

        return operator
        
    def destroy(self):
        "Destroy all gtk widgets contained in self.widgets"
        for w in self.widgets:
            w.destroy()

    def set_active(self, active):
        self.check_button.set_active(active)

    def get_active(self):
        return self.check_button.get_active()

    def set_operator(self, op, value):
        """
        Set the active operator entry in ComboBox for operator choice
        """
        operator_list = self.tool.get_suitable_operators()
        if op == 'IS NULL' and value is False:
            op = 'IS NOT NULL'

        if op in '=' and isinstance(self.tool, FilterBooleanTool):
            if value == True:
                op = 'IS TRUE'
            else:
                op = 'IS FALSE'

        try:
            index = operator_list.index(op.upper())
            self.operator.set_history(index)
        except ValueError, e:
            print "operator '%s' not available in this context" % op.upper()
            print "used: %s -- list: %s" % (op, operator_list)
            raise
            pass

    def get_operator(self):
        """
        return operator set in widget
        """
        return self.operator.get_menu().get_active().get_data('value')

    def get_value(self):
        """
        return value of filter string if any
        """
        return self.field_widget.get_text() 
    
    def set_value(self, value):
        """
        set string for FilterWidget
        """
        
        self.field_widget.set_text(self.tool.string_representation(value))


    def date_changed_cb(self, entry, ):
        """
        date changed: show the new date and set a tooltip
        """
        try:
            dates_ = datetools.string2dates(entry.get_text())
        except:
            entry.set_tooltip_text('')
            self.tool.panel.l.sb(_('incomplete date format'))
            return
            
        dates_ = [dates.format_date(d, locale=dates.default_locale()) for d in dates_ if d]
        text = " - ".join(dates_)
        entry.set_tooltip_text(text)
        self.tool.panel.l.sb(text)


#     def pop_menu(self, wdg, ev, num_button):
#         print "POP_MENU", self, self.menu
#         if ev.button == num_button:
#             self.menu.popup(None, None, None, ev.button, ev.time )
        








