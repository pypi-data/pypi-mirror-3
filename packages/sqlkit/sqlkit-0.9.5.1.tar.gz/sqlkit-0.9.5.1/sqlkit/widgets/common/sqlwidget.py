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

import sys
import re
import os
import datetime
import decimal
import inspect
import gc
import shutil
import warnings

import gtk
import pango
import gobject
from babel import numbers
import sqlalchemy
from sqlalchemy import exceptions, Table, orm
from sqlalchemy.orm import scoped_session, sessionmaker, class_mapper, attributes
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm.mapper import Mapper
from pkg_resources import parse_version 

import sqlkit
from sqlkit import _, exc, layout, debug as  dbg, fields
from sqlkit import layout, debug as  dbg
from sqlkit.layout import map_labels, get_label
from sqlkit.db import minspect, defaults
from sqlkit.widgets.common import completion, sqlfilter, layoutgenerator, dialogs
from sqlkit.misc.utils import Container, str2list
from sqlkit.misc import printing

NUMBERS = (int, float, decimal.Decimal)

class SqlWidget(gobject.GObject):
    """
    The main widget used to edit a table or sqlalchemy selectable, i.e. almost everything you can
    express as table or for which you can provide a mapper or a mapped class.

    You won't use this as such: this is just the parent of SqlTable an SqlMask.
    """
    #### Signals
    __gsignals__ = {
        'record-selected' : (gobject.SIGNAL_RUN_LAST,
                           gobject.TYPE_BOOLEAN,
                           (),
                           ),
        'record-saved'   : (gobject.SIGNAL_RUN_LAST,
                           gobject.TYPE_BOOLEAN,
                           (),
                           ),
        'record-new'   :   (gobject.SIGNAL_RUN_LAST,
                           gobject.TYPE_BOOLEAN,
                           (),
                           ),
        'record-deleted':  (gobject.SIGNAL_RUN_LAST,
                           gobject.TYPE_BOOLEAN,
                           (gobject.TYPE_PYOBJECT,),
                           ),
        'records-displayed' : (gobject.SIGNAL_RUN_LAST,
                           gobject.TYPE_BOOLEAN,
                           (),
                           ),
        'after-flush' :    (gobject.SIGNAL_RUN_LAST,
                           gobject.TYPE_BOOLEAN,
                            # object, session
                           (gobject.TYPE_PYOBJECT , gobject.TYPE_PYOBJECT ),
                            ),
        'after-commit' :    (gobject.SIGNAL_RUN_LAST,
                           gobject.TYPE_BOOLEAN,
                            # object, session
                           (gobject.TYPE_PYOBJECT , gobject.TYPE_PYOBJECT ),
                            ),
        'delete-event' : (gobject.SIGNAL_RUN_LAST,
                           gobject.TYPE_BOOLEAN,
                           (),
                           ),

                            }
    gui_fields = None
    values = None    # real value for foreign key
                     # (when lookup is displeyed instead)
    __metaclass__ = None if not dbg.debug else dbg.LogTheMethods
    records = None
    last_new_obj = None

    def __init__(self, what=None,
                 mapper=None,
                 ## geometry
                 layout = None,
                 layout_nick = 'default',
                 naked=False,
                 geom=(-1,-1),
                 rows=10,
                 addto=None,
                 gui_field_mapping = None,
                 title=None,
                 show=True,
                 icons='',
                 col_width = None,
                 # SQL
                 table=None,
                 tables=None,
                 class_=None,
                 join=None,
                 ro=False,
                 noup=[],
                 sql=None,
                 constraint={},
                 dbproxy = None,
                 order_by=None,
                 limit=200,
                 field_list=None,
                 session=None,
                 metadata = None,
                 ignore_fields = None,
                 hide_fields = None,
                 ## more
                 single=False,
                 nick=None,
                 about_dialog = None,
                 dev=False,
                 xml=False,
                 relationship_mode = 'SINGLE',
                 relationship_path = None,
                 relationship_leader = None,
                 format=None,
                 label_map = None,
                 hooks = None,
                 mode='biud',
                 ):

        """
        :param what: this is the table/mapper/class to be displayed. You are
           encouraged to use it as first argument. The keyword 'what' is
           just here for backward compatibility as the first versiona had
           different keywork for table/classes/mappers

        :param table: the table to be edited. May be a string in which case it will
           be autoloaded or a `sqlalchemy.Table` object. When using table argument
           no info on relationship to other table are passed except those
           contained in the Foreignkey, so you won't be able to show one2many or
           many2many relationships

           If you pass 2 table as in ``movie director`` sqlkit will try to join
           them and build a proper mapper.

           This keyword is now **deprecated** and will disappear in future releases.
           You are encouraged to use the table as first argument istead.

        :param class\_: a sqlalchemy mapped class (eg: that defined via declarative
           layer). The mapper will be automatically found

           This keyword is now **deprecated** and will disappear in future releases.
           You are encouraged to use the class as first argument istead.

        :param mapper: a mapper. All fields will be desumed by introspection

           This keyword is now **deprecated** and will disappear in future releases.
           You are encouraged to use the mapper as first argument istead.

        :param session: the session to be used

        :param dbproxy: a :ref:`dbproxy` object that holds info on metadata and can
           create sessions

        :param metadata: a metadata object needed for introspection if reflection
           is required

        :param hooks: the :ref:`hooks` class to be used for this widget

        :param ro=False:
           if set to True the table is not updateable. Old way to set mode='b'

        :param mode:
           mode for the widget. See :ref:`set_mode <set_mode>` for more explanations

        :param noup=[]:
           a list of field names that will not be allowed to update. The list may be
           also a string space or comma separated

        :param order_by=None: 
           order by column to be used when selecting. Can be 

            * a list of sqlalchemy order_by clause elements
            * a string as would be  set in ordinary SQL statements
            * a string of fields as would be used in filters:
              ``user_id__username`` (note the double_underscore). If you also have
              a relation ``user`` that points to the same table you can use 
              ``user__username`` with the same effect.

        :param limit=200:
           limit attribute to be used selecting

        :param field_list=None:
           a field_list to be shown. This can also be set via "set_field_list". Operate
           via toggling visibility of the columns in Tables or preventing
           autogenerated layout to show.

        :param ignore_fields = None:
           field to be ignores (will be deleted from field list to field_list).
           Can be a list or a comma  separated string.

        :param hide_fields = None:
           Only valid for SqlTable. List of columns to be hidden (but can be
           interactively made to show up from menu). Can be a list or a comma
           separated string.

        :param single=False:
           if a table is opened in single mode, destroying the table quits the gtk
           main loop.

        :param format=format_dict:
           equivalent to using:  .set_format(format_dict).  See :ref:`localization`
           for more info

        :param col_width:
           a dictionary of field_name/width for columns (e.g: {'zip_code' : 6}). It
           can be passed to masks also that will handle on to nested tables. In this
           case if you have a relation with attribute 'address' you may use: 
           {'address.zip_code': 6}

        :param gui_field_mapping: a dict that maps field names to Field classes. You
           only need to set this for non persisted fields, i.e. field that are not
           already defined in the mapper

        :param title:
           the title for the gtk.Window. 

        :param show:
           a boolean to tell if the Window will be visible

        :param dev:
           if a sqlwidget is opened in dev mode and no field_list is passed, the
           primary key is shown even if it's  a serial, if it's not in dev mode it
           will be hidden

        :param naked=False: 
           the table will be rendered without any buttons. It's used in layout when
           you want to add the table/mask to another layout (eg: in
           relationships). Default: False.

        :param addto=None:
           if set must be a container to which the sqlwidget will be added

        :param about_dialog:
           Pass a dialog to invoke when info is called. A gtk.AboutDialog info will be
           created by default if no about_dialog is passed

        :param label_map:
           argument:  label_map dictionary as explained in :ref:`localization`
           Adds a mapping between field_names and msgid/translation for gettext and
           tooltips

        :param layout: 
           string description of the layout as described in :ref:`mask`. It's used
           to generate the layout for SqlMask also for table's
           :ref:`recordinmask`.

        :param layout_nick:
           nick name of a layout to be used. Defaults to ``default``. A layout can
           be registered under a nick via :func:`register layout <sqlkit.db.utils.register_layout>``
           function 

        :param relationship_mode: SINGLE, m2m, m2o, o2m
              
        :param relationship_path: the path needed to join two tables. See sqlalchemy on 'quering
                  with joins'. Used by filter_panel to setup join condition when filtering
                  when relationship_mode is not SINGLE. May be a list or a string:
                  'genres', 'director nationality', ['director','nationality']
        :param relationship_leader: the main sqlmask (sqltable) that "owns" the filter_panel
        """

        gobject.GObject.__init__(self)
        self._ids = {}  # handler for connect to gobjects
        if what:
            if isinstance(what, (basestring, sqlalchemy.Table)):
                table = what
            elif isinstance(what, Mapper):
                mapper = what
            else:
                class_ = what
        else:
            frame = sys._getframe(2)
            info = "Called by '%s' in %s:%s" % (frame.f_code.co_name,
                                                frame.f_code.co_filename, frame.f_lineno)
            warnings.warn("Use of table/tables/class_/mapper keyword is now Depecated\n" +\
                          "place table/class_/mapper as first argument\n%s" % info,
                          DeprecationWarning, stacklevel=3)
                
        if gui_field_mapping:
            self.gui_field_mapping = gui_field_mapping 
        self._format_dict = format
        self.related = Container()
        self.gui_fields = Container(self.gui_fields)
        self.field_widgets = Container()
        self.completions = Container()
        self.label_map = map_labels(buf=label_map, private=True)
        self.icons = icons
        self.col_width = col_width
        self.xml = xml
        self.dev = dev
        # used in self.reload() to prevent expose loop 
        self.reloading = dbg.TraceIt(False, name='reloading')
        self.geom = geom
        self.addto = addto
        self.dbproxy = dbproxy

        self.mapper = self._get_mapper(mapper, table or tables, class_)
        self.metadata = self._get_metadata(metadata, self.mapper)
        ## we can use singular or plural as an option, plural in the code
        if table and not tables:
            tables = table
        self.tables = self._get_table(tables)
        self.session = self._get_session(session)
        self.hooks = hooks or defaults.get_hook(self.tables, instance=True, nick=layout_nick)
        self.nick= self.get_nick(nick)
        self.set_mode(mode, delay=True)
        self.ro = ro
        if ro:
            self.set_mode('b', delay=True)
        self.noup = noup
        self.rows = rows
        self.hidden_fields = hide_fields or []
        self.mapper_info = self.get_fields()
        self.layout   = layout or self._get_layout_from_nick(layout_nick)
        self.field_list = self._parse_fields(field_list)
        self.ignored_fields = self._set_ignored_fields(ignore_fields)
        self._title = self._create_title(title)

        ## create the interface and add obvious constraints
        self.naked = naked
        self.sql   = sql
        self.single = single
        self.limit=limit
        self.relationship_mode = relationship_mode
        self.relationship_path = self._get_relationship_path(relationship_path)
        self.relationship_leader = relationship_leader
        if relationship_leader:
            hid = relationship_leader.connect('delete-event', self.delete_event_cb)
            self._ids['relationship_leader'] = (relationship_leader, hid)
        self.records = []
        self.about_dialog = about_dialog or self.create_about_dialog()
        try:
            self.show(show)
        except exc.DBAPIError, e:
            msg = _("Sorry, problems connecting to remote db. Original error was: \n\n%s" % e)
            raise exc.ConnectionError(msg)
            
        if not relationship_leader:
            self._filter_panel =  sqlfilter.FilterPanel(self, visible=False)
        if hide_fields:
            self.hide_fields(hide_fields)
        self.set_format(format)
        self.query = self.session.query(self.mapper)
        self.defaults = defaults.Defaults(self.tables, metadata=self.metadata, local=True)
        self.order_by = order_by
        self.printing = printing.PrintTool(self)

    def _get_session(self, session):
        """
        return a session suitable for this widget
        """
        from sqlkit.db.proxy import SKSessionExtension

        if not session:
            session = self.dbproxy.get_session()

        if parse_version(sqlalchemy.__version__) < parse_version('0.7'):
            for extension in session.extensions:
                if isinstance(extension, SKSessionExtension): 
                    extension.sk_widgets = (getattr(extension, 'sk_widgets') or []) + [self]
        else:
            try:
                session._sk_emitter.add(self)
            except AttributeError:
                warning.warn("Session does not have '_sk_emitter', signals after-flush "
                             "after-commit and after-flush-postexec are not implemented")
            
        return session

    def _clean_session_extensions(self, *args):
        """
        get rid of any mechanism that was built for 
        """
        if parse_version(sqlalchemy.__version__) < parse_version('0.7'):
            from sqlkit.db.proxy import SKSessionExtension
            for extension in self.session.extensions:
                if isinstance(extension, SKSessionExtension): 
                    extension.sk_widgets.pop(extension.sk_widgets.index(self))
        else:
            self.session._sk_emitter.remove(self)
        
    def _get_mapper(self, mapper, tables, class_=None):

        from sqlkit.db.utils import get_class

        if not mapper and not class_ and get_class(tables):
            class_ = get_class(tables)
        
        if mapper:
            return mapper
        elif class_:
            mapper = class_mapper(class_)
            ## this grants that a class_ that was registered *before* a binding
            ## was active (eg: from sqledit when you only have models.py in nick dir)
            ## gets a correct one. Mailiy needed to automante sqledir nicks 
            if not mapper.local_table.metadata.bind and self.dbproxy.metadata:
                mapper.local_table.metadata.bind = self.dbproxy.metadata.bind
        else:
            mapper = self.dbproxy.get_mapper(mapper, tables)
            
        #self.tables = [mapper.local_table.name]  ## FIXME: what when we have a join?
        if parse_version(sqlalchemy.__version__) < parse_version('0.7'):
            mapper.compile()  # this insures that all attribute gets compiled
        else:
            orm.configure_mappers()
        return mapper

    def _get_metadata(self, metadata, mapper):
        if metadata:
            return metadata
        if self.dbproxy:
            return self.dbproxy.metadata
        if mapper:
            ## FIXME: no good in general? what if you have more that
            ## one metadata in the same session?... boh
            return mapper.local_table.metadata
        
    def _get_table(self, tables):
        from sqlalchemy.sql import Join
        
        if isinstance(tables, Table):
            return tables.name
        if tables:
            return tables.split()[0]  ## FIXME: works for 1 single table
        if self.mapper:
            if isinstance(self.mapper.local_table, Join):
                name = "%s_%s" % (self.mapper.local_table.left, self.mapper.local_table.right)
            else:
                name = self.mapper.local_table.name

            return name

    def _parse_fields(self, field_list):
        if not field_list:
            ### if no layout was defined and no field_list was passed
            ### we don't add PropertyLoader (ManyToMany relations):
            ### we would't know where to represent them.
            ###
            ### If a layout was defined, we add propertyLoader only for SqlMask
            ###
            if self.is_mask() and self.layout:
                get_the_keys = self.mapper_info.all_keys
            else:
                get_the_keys = self.mapper_info.keys
                
            if self.dev:
                new_field_list = get_the_keys()
            else:
                ## I want all fields not ending with _id
                ## *AND* all fields that REFERENCE other keys
                ## i.e.: if you have city_id that references a city I want
                ## to see it, but I don't want to see a sequence normally.
                new_field_list = [f for f in get_the_keys()
                          if not f == 'id' or self.mapper_info.fields[f]['fkey'] ]

        else:
            new_field_list = str2list(field_list) 
        return new_field_list
    
    def _get_relationship_path(self, path):
        """
        relationship_path is the path needed to get from the main sqlwiget to here:
        if movie has an attributes 'genres' that is set as a relation to it, the 'path'
        of the SqlTable of the genres will be: ['genres'].

        It's used in filter widgets
        """

        self.m2m_editable = False
        if not path:
            return []
        
        return str2list(path)
        
    def get_pk(self):
        """
        return the pkeys of the primarytable
        """
        return self.mapper_info.pkeys[self.mapper_info.get_primary_table()]

    def setup_field_validation(self):
        """
        fill self.gui_fields with fileds.Field objects
        """
        raise NotImplementedError
    
###### Filters/constraints
    def add_constraint(self, OR=False, **kwargs):
        """
        Add :ref:`constraints`. A constraint may be expressed via keyworks in django-like
        syntax. Eg.::

           name_like='uno%'
           genres__name__regexp='sto'
           director_id__birth_date__gte='1/1/1970'

        if multiple conditions are passed, they will be ANDed unless 'or_=True'

        A constraint may also be build directly into the self.query object.

        :param OR: the condition will be ORed

        """
        from sqlkit.db.django_syntax import django2query
        self.query = django2query(self.query, self.mapper, OR=OR, **kwargs)
        
    def add_filter_cb(self, event=None, visible=True):
        """
        Pop a Filter Panel, called from menu item
        """
        self.filter_panel.show()

    def add_filter(self, active=True, force_=True, **kw):
        """
        :param active: boolean: make the filter active/inactive

        see :ref:`filters` and ``add_constraint`` above. Note that filter are always 
        ANDed (OR arameter is not available).

        If you have a field_name named 'active', the active parameter will hide it. Use
        keyword ``active__eq`` to bypass it.
        
        """
        self.filter_panel.add_filter(active, force_=force_, **kw)
        
###### Layout

    def _get_layout(self, lay, naked):
        """
        lay may be a definition string or another SqlMask in case the layout has
        just been build by another SqlMask object and we just need to
        add controls and so on
        """
        self.run_hook('on_pre_layout')
        self.get_table_labels()
        
        self.laygen = layoutgenerator.LayoutGenerator(self, naked=naked, lay=lay)
        lay = self.laygen.layout
        self.lay_obj = layout.Layout(lay, addto=self.addto,label_map=self.label_map,
                                     title=self._title, opts='T-')

        if self.xml:
            self.lay_obj.xml('/tmp/m_%s.glade' % self.nick)

        if 'Window' in self.lay_obj.elements:
            self.lay_obj.prop('Window', 'visible', False)

        self.widgets = self.lay_obj.show()

        if 'A.external' in self.widgets:
            external_align = self.widgets['A.external']
            table = external_align.get_parent()
            table.child_set_property(external_align, 'y-options', gtk.EXPAND | gtk.FILL)

        if 'S=tree' in self.widgets:
            internal_align = self.widgets['S=tree']
            table = internal_align.get_parent()
            table.child_set_property(internal_align, 'y-options', gtk.EXPAND | gtk.FILL)

        if self.is_toplevel():
            self.lay_obj.connect(('Window', 'delete-event', self.delete_event_cb))
            if self.geom:
                self.resize(*self.geom)

        self.setup_field_validation()
        
        return (self.lay_obj, self.widgets)
    
    def _get_layout_from_nick(self, nick):
        """
        return a layout for table/nick nick
        """
        if self.is_table():
            # No way at the moment to register a layout for Tables
            return
        from sqlkit.db import get_layout

        ## FIXME: self.master.tables is not really defined. Mau be a string or a list 
        return get_layout(self.tables, nick=nick or 'default')

    def show(self, show):
        """
        create the widget and go on displaying the layout
        """
        self.lay_obj, self.widgets  = self._get_layout(self.layout, self.naked,)
        self.prepare_actions()
        self.prepare_uimanager()
        self.set_mode()
            
        ## only render when dimentions are complete
        lcontainer_name = self.lay_obj.container().el_def
        el_def = re.sub(':.*','', lcontainer_name)

        if show:
            self.widgets[el_def].show()
        self.set_mode()

    def _set_ignored_fields(self, ignored_list):
        """
        Ignored fields will not even be in self.field_list
        """
        ## TODO: verify if I'm really using this. I don;t think I ever documented it...
        ignored_list = str2list(ignored_list)

        if not ignored_list:
            return None
        
        for field_name in ignored_list:
            if field_name in self.field_list:
                self.field_list.remove(field_name)

        return ignored_list
        
    def hide_fields(self, *args):
        """
        """
        self.dialog(type="ok", text=_("Hiding field is only supported for Tables"))
        
    def _get_noup(self, noup=None):
        """return noup set of field_name that are not updateable"""

        return self._noup or set()

    def _set_noup(self, noup):

        if isinstance(noup, (tuple, list, set, frozenset)):
            self._noup = set(noup)
        else:
            if not hasattr(self, '_noup'):
                self._noup = set()
            for x in str2list(noup or ''):
                if x.startswith('-'):
                    x = x.replace('-', '')
                    if x in self._noup:
                        self._noup.remove(x)
                elif x.startswith('-'):
                    x = x.replace('+', '')
                    self._noup.add(x)
                else:
                    self._noup.add(x)
                    
        try:
            self.set_mode() # forces tables to reset editable on columns
        except AttributeError:
            ## actiongroup is not yet ready, but mode will be forced later anyhow
            pass

    noup = property(_get_noup, _set_noup)
    def get_nick(self, nick):
        if not nick:
            if self.tables:
                nick = self.tables
            else:
                nick = self.mapper.tables[0].name
        return nick
            
    def get_fields(self):
        """Fields is a dictionary with info on the fields derived from the
        db via the mapper (inspecting it)
        """
        info = minspect.InspectMapper(self.mapper, noup=self.noup)
        ## fix column_width that may have been passed
        if self.col_width:
            for field_name, value in self.col_width.items():
                if field_name in info:
                    info.fields[field_name]['length'] = value
        return info
        
    def _get_filter_panel(self):

        if self.relationship_leader:
            return self.relationship_leader.filter_panel
        else:
            return self._filter_panel
        
    filter_panel = property(_get_filter_panel)

    def _set_title(self, title):

        if self.is_toplevel():
            self.widgets['Window'].set_title(title)
        self._title = title
        
    def _get_title(self):
        
        if self.is_toplevel():
            return self.widgets['Window'].get_title()
        else:
            return getattr(self, '_title', None)
        
    title = property(_get_title, _set_title)
            
    def grab_focus(self, widget):
        """
        make sure the focus is grabbed so that all validation-related triggers
        update correctly. If the widget cannot get focus, try tb=gtk-save
        """

        sqlwidget = self.relationship_leader or self
        save_widget = sqlwidget.ui_manager.get_widget('/Main/File')
        save_widget.grab_focus()
        
    def sb(self, text, seconds=10, delay=False):
        """
        Write on the status bar if present in this  sqlwidget or in the ``relationship_leader``

        Adds a message in the stack of messages of the status bar, and removes it
        after seconds seconds. If delay=True it uses gobject.idle_add to give
        more chance to be visible (not hidden by other automatic messages)


        :param text: the text to be written
        :param seconds: how may seconds the text should stay visible
        :param delay: boolean. If True message is added in an idle cicle. It means it will be shown
               after other possibly scheduled automatic messages that would hide its visibility.
        """
        try:
            if self.relationship_leader:
                self.relationship_leader.sb(text, seconds=seconds)
            else:
                try:
                    if delay:
                        gobject.idle_add(self.lay_obj.sb, text, seconds)
                    else:
                        self.lay_obj.sb(text, seconds=seconds)
                except Exception, e:
                    #print e, vars(e)
                    pass
        except AttributeError, e:
            ## The widget has been deleted and no self.relationship_leader already emptyed
            pass

    def _create_title(self, title=None):
        if not title:
            try:
                title=self.table
            except:
                title= self.mapper_info.get_primary_table()
        return gobject.markup_escape_text(title)
    
    def get_table_labels(self):
        """
        get labels and tips from the db is they exists
        """
        from sqlkit.db.utils import get_labels_and_tips_from_sqlkit
        if self.tables:
            for table in [t.name for t in self.mapper.tables]:
                self.label_map.update( get_labels_and_tips_from_sqlkit(table, metadata=self.metadata))
            
    def resize(self, width, height):
        """
        Resize the window. It accepts also -1 as value in which case sets
        the current value, so it can be used to change just one dimention.

        """
        Window = self.widgets['Window']
        w, h = Window.get_size()

        if width <= 0:
            width = w

        if height  <= 0:
            height = h
            
        gobject.idle_add(Window.resize, width, height)
        
    def gquit(self, *args):
        gtk.main_quit()
                       
###### Actions/UiManager
    def prepare_actions(self):
        """
        Prepare action needed by UIManager
        """
        self.actiongroup_general = gtk.ActionGroup('General')
        self.actiongroup_update  = gtk.ActionGroup('Update')
        self.actiongroup_insert  = gtk.ActionGroup('Insert')
        self.actiongroup_delete  = gtk.ActionGroup('Delete')
        self.actiongroup_select  = gtk.ActionGroup('Select')
        self.actiongroup_browse  = gtk.ActionGroup('Browse')
        self.actiongroup_print   = gtk.ActionGroup('Print')    
        self.actiongroup_debug   = gtk.ActionGroup('Debug')    

        tip = _('Show all the differences that should be saved to database')
        self.actiongroup_general.add_actions([
            ('File', None, 'File' ),
            ('Modify', None, _('Modify') ),
            ('Go', None, _('Go') ),
            ('Tools', None, _('Tools') ),
            ('Help', None, _('Help') ),

            ('Quit', gtk.STOCK_QUIT, None, '<Ctrl>q', None, self.delete_event_cb),
            ('About', gtk.STOCK_ABOUT, None, None, None, self.about_dialog_cb),
            ('PendingDifferences', None, _('Pending Differences'), None, tip, self.pending_differences_cb),
            ])

        self.actiongroup_update.add_actions([
            ('Save', gtk.STOCK_SAVE, None, '<Ctrl>s', _('Save current record'), self.record_save_cb),
            ])
            
        self.actiongroup_browse.add_actions([
            ('Filters', gtk.STOCK_FIND, _('Filter panel'), None, _('Add filter panel'), self.add_filter_cb),
            ('Reload', gtk.STOCK_REFRESH, _("Reload"), '<Ctrl>r', _('Reload from the database'),
             self.reload_cb),
            ])
        self.actiongroup_select.add_actions([
            ('Forward', gtk.STOCK_GO_FORWARD, None, '<Alt>f', _('Go to next record'), self.record_forward_cb),
            ('Back',   gtk.STOCK_GO_BACK, None, '<Alt>b', _('Go to previous record'), self.record_back_cb),
            ])

        self.actiongroup_print.add_actions([
            ('Print', gtk.STOCK_PRINT, None ),            
            ])

        self.actiongroup_debug.add_actions([
            ('Gtk-tree', gtk.STOCK_EXECUTE, _('Inspect widgets'), '<Ctrl><Alt>i', None, self.show_widget_info),
            ])

    def prepare_uimanager(self):
        """
        Prepare UIManager, actions, and accelerators
        """

        import uidescription

        self.ui_manager = gtk.UIManager()

        if self.is_toplevel():
            self.accel_group = self.ui_manager.get_accel_group()
            self.widgets['Window'].add_accel_group(self.accel_group)

        self.ui_manager.add_ui_from_string(uidescription.GENERAL_UI)
        self.ui_browse_id = self.ui_manager.add_ui_from_string(uidescription.BROWSE_UI)
        self.ui_debug_id = self.ui_manager.add_ui_from_string(uidescription.DEBUG_UI)
        self.ui_print_id = self.ui_manager.add_ui_from_string(uidescription.PRINT_UI)

        self.ui_manager.insert_action_group(self.actiongroup_general, 10)
        self.ui_manager.insert_action_group(self.actiongroup_insert, 11)
        self.ui_manager.insert_action_group(self.actiongroup_delete, 12)
        self.ui_manager.insert_action_group(self.actiongroup_update, 13)
        self.ui_manager.insert_action_group(self.actiongroup_browse, 14)
        self.ui_manager.insert_action_group(self.actiongroup_select, 15)
        self.ui_manager.insert_action_group(self.actiongroup_print, 16)
        self.ui_manager.insert_action_group(self.actiongroup_debug, 17)

        self.ui_manager.connect('connect-proxy', self.uimanager_connect_proxy)
        ## pack menu and toolbar if it's a toplevel
        if 'V.header' in self.widgets:
            header = self.widgets['V.header']
            menu    = self.ui_manager.get_widget('/Main')
            toolbar = self.ui_manager.get_widget('/TbMain')
            header.add(menu)
            header.add(toolbar)

    def uimanager_connect_proxy(self, uimgr, action, widget):

        tooltip = action.get_property('tooltip')
        if isinstance(widget, gtk.MenuItem) and tooltip:
            widget.set_tooltip_text(tooltip)

    def set_mode(self, mode=None, reset=False, delay=False):
        """
        .. _set_mode:

        :param mode: the mode as explained below. If None, mode will be refreshed to last *declared*
           state (i.e.: reguardless of what you may have changed by hand acting on actiongroups).
        :param reset: if True the mode will be completely reset. Needed to make the mode
            of a related table independent from the mode of the master
        :param delay: if True, the mode is set but interface is not immediately updated


        Set mode for this widget. Mode can be a string composed with the following letters that
        correspond to permissions possibly preceded by ``+`` or ``-``.

         :s: SELECT. The user can view the records *already selected*
             (i.e. use Forward/Backward) or set by ``set_records``. This is *always* granted and
             as such it's pointless to set it (or revoke it)
         :i: INSERT. The user can insert new records
         :u: UPDATE. The user can update records
         :d: DELETE. The user can delete records
         :b: browse. The user can use the filter panel

        If mode start with + or - the following permissions are granted/revoked for the widget
        by adding or removing from the modes already present. If no sign is used the mode is set.

        ``mode`` is a property, you can set it directly: ``self.mode = 'b'``

        The mode influences permission by setting menu entries active or not. It's not acting on
        the session. If an object has been inserted in the session a simple update operation
        can let it be inserted. This is by design.

        Related table inheritate the same mode but you can programmatically reset it and make it
        independent from the master using option reset=True. 

        *Implementation*

        Mode are implemented acting on uimanager/actionsgroup. You may read :ref:`uimanager`

        .. note::

           at present it's not possible to insert a record in a table that is not updatable
        """
        known_modes = 'iudbD'

        if not hasattr(self, '_mode'):
            self._mode = set([x for x in known_modes])

        if reset:
            if not mode or (isinstance(mode, basestring) and re.match('[-+]', mode)):
                model_mode = self._mode
            else:
                model_mode = mode
            self._mode = set(x for x in model_mode)

        if mode:
            if isinstance(mode, set):
                if not reset:
                    self._mode = mode 
            elif mode.startswith('+'):
                ## add a permission
                for x in mode.replace('+', ''):
                    self._mode.add(x)
            elif mode.startswith('-'):
                ## deletes a permission
                for x in mode.replace('-', ''):
                    if x in self._mode:
                        self._mode.remove(x)
            else:
                ## entirely resets the permission
                for x in known_modes:
                    if x in mode:
                        self._mode.add(x)
                    else:
                        if x in self._mode:
                            self._mode.remove(x)

        if not delay:
            self.actiongroup_insert.set_sensitive('i' in self._mode)
            self.actiongroup_update.set_sensitive('u' in self._mode)
            self.actiongroup_delete.set_sensitive('d' in self._mode)
            self.actiongroup_browse.set_sensitive('b' in self._mode)
            self.actiongroup_debug.set_sensitive('D' in self._mode)

    def get_mode(self):
        return self._mode
    
    mode = property(get_mode, set_mode)
                
###### Saving
    def record_delete(self, widget=None):
        """invokes the validator before DELETing a record"""
        pass
    
    def record_save_cb(self, widget, event=None):
        """Save the record and invokes the validator before UPDATE/INSERT a record
        """
        self.get_toplevel().set_focus(None)
        try:
            self.record_save()
        except (exc.DialogValidationError, exc.CancelledAction), e:
            pass
    
    def record_new_cb(self, widget, event=None):
        """Save the record and invokes the validator before UPDATE/INSERT a record
        """
        try:
            self.record_new()
        except (exc.DialogValidationError, exc.CancelledAction):
            return True
    
    def record_save_new_cb(self, action):
        """
        Save the record as a new record, ie letting pk not be set 
        """
        self.record_save_new()
        
    def record_add(self, record):
        """
        Add a record to the SqlWidget
        """
        self.records += [record]
        self.session.add(record)

    def commit(self, message=_('Saved')):
        """
        run session.commit() and take care of possible exceptions

        :param message: a message to be written in the status bar (default: Saved)
        """
        if self.ro:
            return
        try:
            ## when session.autocommit = False, a transaction is automatically started
            if self.session.autocommit:
                self.session.begin()

            self.session.commit()
            self.emit('record-saved', )
            self.run_hook('on_record_saved')
            self.sb(message, seconds=3)

        except (exceptions.DBAPIError, exceptions.FlushError), e:
            if not self.commit_error_handler(e):
                self.session.rollback()
                raise exc.HandledRollback(str(e))

    def commit_error_handler(self, e):
        """
        communicate the problem to the user
        return True to prevent rollback
        """
        if isinstance(e, exceptions.IntegrityError):
            # TIP: message in the status bar when a commit error is handled
            msg = _("Error while writing to the database. \nOriginal error was: \n%s") % e
            self.message(type='error', text=_(msg))
            self.sb(str(e))

        elif isinstance(e, exceptions.ProgrammingError):
            # TIP: Error while saving into a table w/o permission
            msg = _("A programming error was received from the backend:\n%s") % e
            if re.search('permission denied', msg, re.I):
                msg = "Access was denied while accessing one of the tables (%s)" % e
            self.message(type='error', text=msg)
            self.sb(e.orig)

        elif isinstance(e, exceptions.DBAPIError):
            # TIP: message in the status bar when a commit error is handled
            self.message(type='error',
                         text=_("%s - Dirty objects: %s - New objects: %s") % \
                         (str(e.orig),len(self.session.dirty),len(self.session.new)))
            self.sb(e.orig)

        elif isinstance(e, exceptions.FlushError):
            # TIP: message in the status bar when a commit error is handled
            msg = _("Error while writing to the database: \n" \
                    "are you 'saving as new' an already known record?\n" + \
                    "original error was: \n%s") % e
            self.message(type='error', text=_(msg))
            self.sb(e)

        return False  # i.e.: rollback

    def get_value(self, field_name, shown=False):
        """
        return the value from the widget

        :param field_name: the field_name
        :param shown: boolean: in case field is a foreign key, ``True`` indicates we want the
             dislayed value rather than the real one

        """

        ## to be overwritten by Mask & Table
        return NotImplementedError
    
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

        #to be overwritten by Mask & Table
        return NotImplementedError
    
    def has_changed(self, field_name):
        """
        return the value from the widget
        """
        
        if field_name not in self.gui_fields:
            dbg.write("%s Non in gui_fields %s" % (field_name, self.gui_fields.keys()))
            raise sqlkit.exc.FieldNotInLayout("field_name: %s" % (field_name))

        field = self.gui_fields[field_name]
        
        return field.has_changed()

    def record_has_changed(self):
        """
        check if any data has been written in the fields after
        record display. Uses field.has_changed()
        """
        ## this is needed since it's hard to say if an instance has been modified
        ## eg: a new item is added to the session, no editing is done. A reload is issued
        ## I want to avoid the dialog: do you want to save?
        ## session.dirty would (correctly) say a commit is needed
        
        if not self.current:
            return False

        obj = self.current
        
        for sqlwidget in self.related:
            if sqlwidget.record_has_changed():
                return True

        for field in self.gui_fields:      
            if not field.editable:
                continue
            try:
                if field.has_changed():
                    return True

            except exc.ValidationError, e:
                return True

        return False

    def save_unsaved(self, refresh=True, skip_new=False, skip_check=False, proceed=True):
        """
        Check if it needs saving. In case ask for confirmation and proceed.
        This triggers both session changes *AND* changes to the current mask that
        may not be in the session.

        :param skip_check: we already know it needs saving. Passed to unsaved_changes_exists
        :param skip_new: skip_new may be an object whose changes we disregard (see unsaved_changes_exist)
        Return False if cancel is pressed
        """
        response = True
        if self.unsaved_changes_exist(skip_new=skip_new) or skip_check:
            dialog = UnsavedDataDialog(self)
            response = dialog.run()

            if response == gtk.RESPONSE_CANCEL:
                pass

            if response == gtk.RESPONSE_YES:
                if proceed:
                    self.record_save(ask=False)
            
            ## you don't want to save. Let's prevent a delayed commit
            ## we don't need to care about deleted becouse when you delete
            ## the commit is immediate
            if response == gtk.RESPONSE_NO:
                self.discard_changes()
     
        return response

    def discard_changes(self):
        """
        Discard any changes in the session, refreshing all objects
        """
        for obj in self.session.dirty:
            if obj in self.session:
                self.session.refresh(obj)

        for obj in self.session.new:
            # when you have several objects in the session.new this test *IS* needed since
            # the first one expunge may cause another one to be expunged too.
            if obj in self.session.new:  
                self.session.expunge(obj)

        self.last_new_obj = None  ## FIXME: unsure...
        
    def unsaved_changes_exist(self, skip_new=False, skip_check=False):
        """
        check if session needs committing by looking dirty, deleted and new
        skip_new: skip_new may be an object that we are not interested in saving
                  new object that where not changed but have default values fall here
        """
        # skip_check is passed to Mask.unsaved_changes_exists
        if self.session.dirty:
            for dirty in self.session.dirty:
                if self.session.is_modified(dirty, passive=True):
                    return True
        if self.session.deleted:
            return True

        if self.session.new:
            for obj in self.session.new:
                if obj is skip_new:
                    self.sb(_("Discarding new obj"), seconds=3)
                    continue
                if self.session.is_modified(obj, passive=True):
                    return True

        return False
    
###### Validation
    def digits_check_input_cb(self, widget, event):
        """
        prevents the possibility of inputting wrong chars
        """
        key = gtk.gdk.keyval_name (event.keyval)

        if key in ('KP_Decimal',) and numbers.get_decimal_symbol() == ",":
            event = gtk.gdk.Event(gtk.gdk.KEY_PRESS)
            event.keyval = gtk.keysyms.comma
            event.window = widget.window
            
            widget.emit('key-press-event', event)
            return  True

        if key in ('KP_Enter',):
            event = gtk.gdk.Event(gtk.gdk.KEY_PRESS)
            event.keyval = gtk.keysyms.Return
            event.window = widget.window
            
            widget.emit('key-press-event', event)
            return  True

        if (event.state | gtk.gdk.CONTROL_MASK):
            return 
   
        KEYPAD_KEYS = '(KP_[0-9]|KP_Add|KP_Decimal|KP_Subtract|comma'
        ONLYDIGITS="%s|[0-9.,]|BackSpace|Left|Right|F1|period|Tab|Up|Down|Return|Esc)"

        if not re.match (ONLYDIGITS % KEYPAD_KEYS, key):
            self.sb(_('Char %s is not accepted in numeric context') % key)
            return True

    def record_validate(self, obj=None, single_fields=True, related=None):
        """
        any validation should live here
        single_fields=bool validation of single fields is done here for table 
                           but in  mask2obj for Masks
                           single_fields determines if check for single fields is done
        returns the validation_error dict to propagate the error info upward
        """
        # if not hasattr(self, 'validation_errors') or related:
        # masks pass throught mask2obj that creates self.validation_errors. I must not discard it
        # in the other cases I neeed to start from zero
        if single_fields or related:
            self.validation_errors   = {}
            self.validation_warnings = {}

        if obj is None:
            obj = self.get_current_obj()
            if obj is None:
                return {}

        for sqlwidget in self.related:
            self.validation_errors.update(
                sqlwidget.record_validate(related=sqlwidget.relationship_path))
            self.validation_warnings.update(sqlwidget.validation_warnings)
            
        if single_fields:
            self.record_validate_fields(obj)

        try:
            self.run_hook('on_validation')
        except exc.ValidationError, e:
            self.add_validation_error(e)

        if related:
            return self.validation_errors

        if self.validation_errors: # just one error dialog
            dialog = ValidationErrorDialog(self)
            dialog.run()
            #self.validation_error_dialog()
    
        if self.validation_warnings: # just one error dialog
            dialog = ValidationWarningDialog(self)
            dialog.run()

    def add_validation_error(self, error, field_name=None):
        """
        keep track of the error in self.validation_errors/validation_warnings
        so that a further process can collect them and present them to the user

        :param error:   the ValidationError or an error message string
        :field_name:    the field_name to which the error refers. Defaults to 'record validation'
        """
        if not field_name:
            ## TIP: the general validation for the record
            field_name = _('record validation') # a key to be used in self.validation_errors

        if isinstance(error, basestring):
            error_message = error
        else:
            error_message = str(error)
            
        if isinstance(error, exc.ValidationWarning):
            error_dict = self.validation_warnings
        else:
            error_dict = self.validation_errors

        if not field_name in error_dict:
            error_dict[field_name] = []

        error_dict[field_name] += [error_message]

        self.sb(error_message, seconds=30)

    def add_not_null_error(self, field_name):
        """
        simple way to add a not nullable field error
        
        :param field_name: the field_name that cannot be nullable
        """
        error = exc.NotNullableFieldError(field_name, master=self)
        self.add_validation_error(error, field_name)
        
    def record_validate_fields(self, obj):
        """
        Validate any fields in self.gui_fields
        """
        for field in self.gui_fields:
            if not field.editable:
                continue
            field_name = field.field_name
            try:
                if field.mapper:   # persisted fields, mask2obj has already cleaned  them
                    value = getattr(obj, field_name)
                    self.gui_fields[field_name].validate( value , clean=True)
                else:              # fields only present in the GUI, value is not in obj
                    value = self.gui_fields[field_name].get_value()
                    self.gui_fields[field_name].validate( value , clean=True)

            except exc.ValidationError, e:
                self.add_validation_error(e, field_name=field_name)

        
###### Hooks
    def run_hook(self, mode, *args, **kw):
        """
        look for a possible hook and call it.
        :param mode: the hook type (eg.: set_value, completion...)
        :param climb: boolean: should I climb relationship_path to get other sqlwidgts' hooks?
        """
        # climb: it's a flag that determines if I must climb the relationship and find
        # others possible hooks in relationship_leaders
        climb = kw.pop('climb', True)

        if self.relationship_leader in (None, self) or climb == False:
            hook_name = "%s" % (mode)
            sqlwidget = self
        else:
            self.run_hook(mode, climb=False, *args, **kw)  # hooks defined for the related table
            hook_name = "%s__%s" % (mode, '__'.join(self.relationship_path))
            sqlwidget = self.relationship_leader 

        if 'field_name' in kw:
            hook_name += "__%(field_name)s" % kw

        if hasattr(sqlwidget.hooks, hook_name):
            if 'field_name' in kw:
                return getattr(sqlwidget.hooks, hook_name)(sqlwidget, kw['field_name'], *args)
            else:
                return getattr(sqlwidget.hooks, hook_name)(sqlwidget, *args)
    
###### Callback
    def clear_cb(self, *args):
        self.clear()

    def reload_cb(self, widget):
        """
        issue a reload operation on master. Call back of reload button
        """
        self.grab_focus(widget)
        try:
            self.reload( )
        except exc.DialogValidationError, e:
            return True

    def record_forward_cb(self):
        """
        it doesn't make any sense here, but we need it to prevent
        _add_actions_to_button from failing
        """
        pass

    def record_back_cb(self):
        """
        it doesn't make any sense here, but we need it to prevent
        _add_actions_to_button from failing
        """
        pass
    
    def destroy(self):
        """
        Destroy the widget
        """
        if 'Window' in self.widgets:
            ## This sqlwidget owns a toplevel Window. Destroying that one triggers
            ## delete_event_cb, that emits 'delete'event'
            event = gtk.gdk.Event(gtk.gdk.NOTHING)
            self.widgets['Window'].emit('delete-event', event)
        else:
            self.emit('delete-event')
        
    def delete_event_cb(self, *args):
        """
        Quit operations: check if need to save first
        """
        try:
            self.record_save()
        except (exc.DialogValidationError, exc.CancelledAction), e:
            return True
        
        self._clean_session_extensions()
        for obj, hid in self._ids.values():
            obj.disconnect(hid)
        del self._ids

        self.emit('delete-event')
        ## get rid of records automatically created by record_new if they're 
        ## not yet persisted 
        if self.current and self.current in self.session.new:
            self.session.expunge(self.current)

        if 'Window' in self.widgets:
            self.widgets['Window'].destroy()
        if self.single:
            self.gquit()
        attrs = [
            'about_dialog',
            'accel_group',
            'actiongroup_browse',
            'actiongroup_debug',
            'actiongroup_delete',
            'actiongroup_general',
            'actiongroup_insert',
            'actiongroup_print',
            'actiongroup_select',
            'actiongroup_update',
            'addto',
            'col_width',
            'completions',
            'constraint',
            'current',
            'current_idx',
            'dbproxy',
            'defaults',
            'dev',
            'field_list',
            'field_widgets',
            'filter_panel',
            'geom',
            'gui_fields',
            'hidden_fields',
            'hooks',
            'icons',
            'ignored_fields',
            'label_map',
            'labels',
            'laygen',
            'lay_obj',
            'layout',
            'limit',
            'm2m_editable'
            'mapper',
            'mapper_info',
            'metadata',
            'modelproxy',
            'last_new_obj',
            '_mode',
            'naked',
            'nick',
            '_noup',
            '_order_by',
            '_order_by_join_args',
            'printing',
            'query',
            'records',
            'related',
            'relationship_leader',
            'relationship_mode',
            'relationship_path',
            'reloading',
            'ro',
            'rows',
            'session',
            'single',
            'sql',
#             'tables',
            '_title',
            '_filter_panel',
            'ui_browse_id',
            'ui_debug_id',
            'ui_manager',
            'ui_print_id',
            'widgets',
            'views',
            'xml',
            ]
        for at in attrs:
            try:
                delattr(self, at)
            except (NameError, AttributeError), e:
                pass
#        ## .sb() may have added a collback with 
#        self.relationship_leader = None
        gc.collect()

    def pending_differences_cb(self, menu=None):

        dialog = UnsavedDataDialog(self, type_='ok', msg=_('Unsaved differences'), expanded=True)
        response = dialog.run()
        
###### Record browsing 
    def clear(self, widget=None):
        """clear the mask for a new record"""
        pass
    
    def reload(self, limit=None, display=True, order_by=None, OR=False, **kwargs):
        """
        reload the data from the database taking all filter/constraints into
        consideration 

        :param limit: add a LIMIT clause (integer) to limit number of returned
            records. Permanent effect
        :param order_by: reset order_by and apply when reloading. Permanent effect.
        :param OR: (boolean, default False) as in ``add_constraint`` you can specify if
                   conditions as in kwargs below should be ORed or ANDed (default)
        :param kwargs: any filters accepted by the :ref:`django-syntax` and by add_filter

        sql may be a tuple (sql_statement, bind_params) or just a sql_statement
        """
        from sqlkit.db.django_syntax import django2query
        if limit:
            self.limit = limit

        query = self.query.filter(None)

        ## order_by
        if order_by:
            self.order_by = order_by
            
        if self.order_by:
            if self._order_by_join_args:
                query = query.reset_joinpoint().join(self._order_by_join_args)
            query = query.order_by(*self.order_by)

        ## filters
        try:
            query = self.filter_panel.add_filter_conditions(query)
        except exc.ParseFilterError, e:
            self.records = []
            return

        if kwargs:
            query = django2query(query, self.mapper, OR=OR, **kwargs)

        if self.limit:
            query = query.limit(self.limit)
                
        self.session.expunge_all()
        self.last_new_obj = None

        if self.is_mask():
            self.current = None
            self.clear(check=False)
        try:
            self.records = query.all()
        except exceptions.ProgrammingError, e:
            # TIP: reloading data from the database
            msg = _("A programming error was received from the backend:\n%s") % e
            if re.search('permission denied', msg, re.I):
                msg = "Access was denied while accessing one of the tables (%s)" % e
            self.message(type='error', text=msg)
            self.sb(e.orig)
            return
        except exceptions.InterfaceError, e:
            ## the connection may be closed and a retry could restore it
            if re.search('closed', str(e), re.I):
                self.records = query.all()
            
        if display:
            self.record_display(check=False)

        length = len(self.records)
        ## after a reload the transaction will stay opend if session.autocommit=False
        ## in postgres this will be evident by "idle in transaction" state of he process
        ## that will inhibit a number of operation (eg.: altering tables)
        ## FIXME: whe we have m2m relation this is not enought, I open some table
        ## and I don't understand where...
        ## nice info here: http://wiki.dspace.org/index.php/Idle_In_Transaction_Problem
        self.session.rollback()

        self.set_mode()
        return length

    def set_records(self, records=None, pk=None):
        """
        set 'records' as the list of record to manage

        :param records: use 'records'  as the list of records
        :param pk: use primary key pk as te pk to show (TODO make it work with composite pks)
        """
        if not records and pk:
            records = self.get_by_pk(pk)
            
        self.records = records
        self.last_new_obj = None
        self.record_refresh()

    def get_by_pk(self, pk):
        """
        Return an object of self.class_ filtered by pk
        """

        query = self.query.autoflush(False)
        record = query.filter_by(**{str(self.get_pk()[0]) : pk}).all()
        return record
    
    def record_refresh(self):
        """to be overloaded: 
        """
        self.emit('records-displayed')
        pass

#     def reload_one(self,field, value):
#         """compact way to view a single record or records with a single property"""

#         sql = "%s = :%s" % (field, field)
#         bind_parameters = {field : value}
        
#         self.reload(  (sql, bind_parameters)  )
    
    def get_new_object(self, session=True, obj=None):
        """create a new object from the class of the mapper and  place it in the session

        :param session: (boolean) if True, add to session
        :param obj: the new obj (default None: it will be created an empty self.mapper.class_ instance)
        
        """
        new_obj = obj or self.mapper.class_()

        if session:
            self.session.add(new_obj)
        return new_obj

    def _set_order_by(self, order_by):
        """
        May be an order_by clause element or a string, with comma separated fields + ASC|DESC
        """
        from sqlalchemy.sql.expression import desc
        from sqlkit.db.django_syntax import django2components

        self._order_by_join_args = None
        if isinstance(order_by, basestring):
            order = []
            for tocken in order_by.split(','):
                order_list = tocken.split()
                field_name = order_list[0]

                #col0 = getattr(self.mapper.class_, field_name)
                ## try to add a join for an order by on a field in a related table
                joins, op, op_str, value, col, join_args = django2components(self.mapper, { field_name: None})
                #assert col0 == col, "django2components does not lead to the same result as getattr"
                if join_args:
                    ## it will be evaluated at reload-time
                    self._order_by_join_args = join_args

                if len(order_list) > 1:
                    direction = order_list[1]
                    if direction.upper() == 'DESC':
                        col = desc(col)
                order += [col]
            self._order_by = order
        else:
            # assume its already a column
            if isinstance(order_by, list):
                self._order_by = order_by
            else:
                self._order_by = [order_by]

    def _get_order_by(self):
        return self._order_by

    order_by = property(_get_order_by, _set_order_by)
    
####### Dialog
    def dialog(self, type='ok-cancel', text='', title='', layout=None, icon='gtk-dialog-question'):
        """
        pop a dialog modal and transient

        :param type: ok, ok-cancel, yes-no-cancel, ok-apply-cancelx
        :param text: the text that should be used (uses markup)
        :param title: the title of the dialog
        :param layout: a possible layout.Layout specification
        :param icon: the icon (defaults to 'gtk-dialog-question')

        """
        if not layout:
            layout = 'i=%s:6 l=message' % icon
            

        dialog, l = self.lay_obj.dialog(layout=layout, title=title,
                                        type=type, show=False)
        if 'l=message' in l.widgets:
            l.prop(('l=message', 'use_markup', True))
            l.widgets['l=message'].set_text(text)

#         l.widgets['l=a'].set_markup(
#             '<span size="14000">%s</span>' % text)
        dialog.show_all()
        response = dialog.run()
        dialog.destroy()
        return response
    
    def message(self, text='', type='question'):
        self.response = None
        dialog = self.lay_obj.message(text=text, type=type)
        #dialog.connect('response', self.response_cb )
        self.response = dialog.run()
        dialog.destroy()
        return dialog
    
    def about_dialog_cb(self, menuItem):
        """
        The about dialog
        """
        self.about_dialog.run()
        self.about_dialog.destroy()
        
    def create_about_dialog(self):
        """
        Create a default AboutDialog
        """
        def func(dialog, link, user_data):
            import webbrowser
            webbrowser.open(link)
            
        about_dialog = gtk.AboutDialog()
        gtk.about_dialog_set_url_hook(func, None)
        about_dialog.set_authors(["Sandro Dentella <sandro@e-den.it>"])
        about_dialog.set_license("GPL v.3")
        about_dialog.set_version(sqlkit.__version__)
        about_dialog.set_name("sqlkit")
        about_dialog.set_website("http://sqlkit.argolinux.org")
        about_dialog.set_website_label("http://sqlkit.argolinux.org")
        return about_dialog
        #dialog.show()
        

###### Misc
    def export(self, menuItem):
        self.dialog(type='ok',
                    text=_("Sorry, export is implemented only for table view"))

    def get_field_type(self, field_name):

        try:
            return self.gui_fields[field_name].type
        except AttributeError:
            return self.mapper_info.fields[field_name]['type']

    def get_label(self, field_name, gtk_label=False):
        """
        return field_name translated according to map_label + gettext

        :param gtk_label: double any occurrence of '_'  as gtk labels 'eat' them
        """
        label = get_label(field_name, layout=self.lay_obj)
        if gtk_label:
            return _(label).replace('_', '__')
        return _(label)

    def set_current(self, pk=None):
        """retrieve a record and set it as current
        """
        raise NotImplemented
    def set_format(self, format_dict):
        """
        set_format(format_dict). format_dict is a dictionary whose key is the
        field_name and the value is the format of the column. Format_dict can
        have keys that do not correspond to any field in the widget. That
        makes it possible to reuse a format dict.

        The format dict is passed to related widgets as well.

        See :ref:`localization` for more info

        :param format_dict: a dict of field_name/format strings

        """
        self._format_dict = format_dict
        if not format_dict:
            return

        for field_name, format in format_dict.items():
            if field_name in self.gui_fields:
                if isinstance(format, tuple):
                    format, locale = format
                    self.gui_fields[field_name].locale = locale

                self.gui_fields[field_name].format = format

        for widget in self.related:
            widget.set_format(format_dict)
            
        
    def add_temporary_item(self, item, menu, position=0, separator=False):
        """
        .. _add_temporary_item:
          
        Adds an action to a menu and removes it with 'selection-done'

        :param item: the gtk.MenuItem that must be added
        :param menu: the menu where the item needs to be added
        :param position: the position where to insert the item (default: 0)
        :param separator: boolean: add a separator (not implemented)
        """
        if not menu:
            return
        
        def remove_widget_cb(menu, item):
            menu.remove(item)

        item.show()
        menu.insert(item, position)
        menu.connect('selection-done', remove_widget_cb, item)
        if separator:
            self.add_temporary_item(gtk.SeparatorMenuItem(), menu, position=position+1)
        
###### Checks
    def is_mask(self, obj=False):
        """
        Return True if the sqlwidget is a Sqlmask
        """
        ## bad way to prevent chicken and eggs import problems 
        from sqlkit.widgets import SqlMask
        if obj == False: ## obj may be an empty str: ''
            obj = self
        return isinstance(obj, SqlMask)
    
    def is_table(self, obj=False):
        """
        Return True if the sqlwidget is a SqlTable
        """
        ## bad way to prevent chicken and eggs import problems 
        from sqlkit.widgets import SqlTable
        if obj == False: ## obj may be an empty str: ''
            obj = self
        return isinstance(obj, SqlTable)
    
    def is_fkey(self, field_name):
        """
        return True if this field is a foreign key
        """
        try:
            return self.mapper_info.is_fkey(field_name)
        except AttributeError:
            return None

    def is_primary(self, field_name):
        """
        return True if this field is a Primary Key
        """
        return self.mapper_info.is_primary(field_name)

    def is_loader(self, field_name):
        """
        True if field_name is a loader for a related table
        """
        return self.mapper_info.is_loader(field_name)

    def is_string(self, field_name):
        """
        Return true if this field is a String type
        """
        try:
            return self.mapper_info.is_string(field_name)
        except AttributeError, e:
            return isinstance(self.gui_fields[field_name], fields.VarcharField)

    def is_date(self, field_name):
        """
        Return true if this field is  date
        """
        try:
            return self.mapper_info.is_date(field_name)
        except AttributeError:
            return self.gui_fields[field_name].type == datetime.date

    def is_datetime(self, field_name):
        """
        Return true if this field is  datetime
        """
        try:
            return self.mapper_info.is_datetime(field_name)
        except AttributeError:
            return self.gui_fields[field_name].type == datetime.datetime

    def is_time(self, field_name):
        """
        Return true if this field is time
        """
        try:
            return self.mapper_info.is_time(field_name)
        except AttributeError:
            return self.gui_fields[field_name].type == datetime.time

    def is_interval(self, field_name):
        """
        Return true if this field is time
        """
        try:
            return self.mapper_info.is_interval(field_name)
        except AttributeError:
            return self.gui_fields[field_name].type == datetime.interval

    def is_integer(self, field_name):
        """
        Return true if this field is integer
        """
        try:
            return self.mapper_info.is_integer(field_name)
        except AttributeError:
            return self.gui_fields[field_name].type in (int, long)

    def is_float(self, field_name):
        """
        Return true if this field is float
        """
        try:
            return self.mapper_info.is_float(field_name)
        except AttributeError:
            return self.gui_fields[field_name].type == float

    def is_numeric(self, field_name):
        """
        Return true if this field is numeric (rendered as Decimal)
        """
        try:
            return self.mapper_info.is_numeric(field_name)
        except AttributeError:
            return self.gui_fields[field_name].type is decimal.Decimal

    def is_number(self, field_name):
        """
        Return true if this field is a number (int, float or Decimal)
        """
        try:
            return self.mapper_info.is_number(field_name)
        except AttributeError:
            return self.gui_fields[field_name].type in NUMBERS

    def is_boolean(self, field_name):
        """
        Return true if this field is boolean
        """
        try:
            return self.mapper_info.is_boolean(field_name)
        except AttributeError:
            return self.gui_fields[field_name].type == bool

    def is_enum(self, field_name):
        """
        Return true if this field is to rendered as enum
        """
        try:
            return self.mapper_info.is_enum(field_name)
        except AttributeError:
            return isinstance(self.gui_fields[field_name], fields.EnumField)

    def is_image(self, field_name):
        """
        Return true if this field is image
        """
        try:
            return self.mapper_info.is_image(field_name)
        except AttributeError:
            False

    def is_file(self, field_name):
        """
        Return true if this field is image
        """
        try:
            return self.mapper_info.is_file(field_name)
        except AttributeError:
            False

    def is_nullable(self, field_name):
        """
        Return true if this field is nullable
        """
        return self.gui_fields[field_name].nullable

    def is_editable(self, field_name):
        """
        Return true if this field is  date
        """
        #edit = self.mapper_info.fields[field_name]['editable']
        edit = self.gui_fields[field_name].editable
        if not edit:
            # you probably explicitely set it (via noup?)
            return False

        ## now if the field is editable, it depends on mode of the widget
        ## and state of self.current

        if self.current in self.session.new:
            return 'i' in self._mode
        elif 'u' in self._mode:
            return 'u' in self._mode
            
        return False


    def is_text(self, field_name):
        """
        Return true if this field is Text or was forced gtk.Text
        """
        import sqlalchemy.types as sqltypes
        
        try:
            if self.laygen.fields_in_layout[field_name].startswith('TX'):
                return True
        except:
            pass
        try:
            return self.mapper_info.is_text(field_name)
        except AttributeError:
            return isinstance(self.gui_fields[field_name], fields.TextField)

    def is_toplevel(self):
        """
        return a boolean indicating if the widget is a toplevel widget
        """
        return 'Window' in self.widgets
    
    def get_toplevel(self):
        """
        return the toplevel for this SqlWidget
        """
        try:
            return self.widgets['Window']
        except KeyError, e:
            try:
                return self.relationship_leader.get_toplevel()
            except AttributeError, e:
                return None
        
    def fkey_is_valid(self):
        """
        return True if current editable -if exists- has a value that does not need validation
        """
        ## Overridden by SqlMask/SqlTable
        raise NotImplementedError
    
    def get_current_obj(self):
        """
        Return the corrently edited obj. Note that in Table widgets,
        selection can already be elsewhere (as in on_selection_change).

        """
        ## Overridden by SqlMask/SqlTable
        raise NotImplementedError
    
###### debug
    def show_mapper_info(self, *args):
        from sqlkit.debug import gtk_dbg
        gtk_dbg.ShowMapperInfo(self.mapper_info)
        
    def show_widget_info(self, *args):
        from sqlkit.debug import gtk_dbg
        gtk_dbg.show_widgets(self.widgets['Window'])
        
    def show_class_info(self, *args):
        from sqlkit.debug import gtk_dbg
        gtk_dbg.ShowClassInfo(self) 
        
    def mostra(self, what):
        """
        debug: show all attribute of an object
        """
        if isinstance(what, int):
            obj = self.records[what]
        else:
            obj = what
            
        for attr in self.field_list:
            print attr, getattr(obj, attr)
            
    

    def show_field_info(self, wdg, field_name):
        """
        Pop a dialog to give info on the selected field
        """

        dialog, lay = self.lay_obj.dialog(layout="TVS=info", type='ok', title="Info on %s" % field_name)

        tv = lay.widgets['TV=info']
        model = gtk.ListStore(str, str)
        tv.set_model(model)
        tv.set_property('width-request', 210)
        tv.set_property('height-request', 320)
        
        cell1 = gtk.CellRendererText()
        cell2 = gtk.CellRendererText()

        tc1 = gtk.TreeViewColumn(_("Property"), cell1, text=0)
        tc2 = gtk.TreeViewColumn(_("Value"), cell2, text=1)

        tv.append_column(tc1)
        tv.append_column(tc2)
        tv.show_all()
        
        for key in ('table_name', 'name', 'db_type', 'col_spec', 'fkey', 'default',
                    'pkey', 'nullable', 'editable', 'length'):
            miter = model.append()
            try:
                if key == "db_type":
                    model.set(miter,
                              0,  key,
                              1, self.mapper_info.fields[field_name][key].__name__)
                elif key == "fkey":
                    fkeys = self.mapper_info.fields[field_name]['fkey']
                    model.set(miter,
                              0,  key,
                              1, ",".join(x.target_fullname for x in fkeys))
                else:
                    model.set(miter,
                              0,  key,
                              1, self.mapper_info.fields[field_name][key])
            except AttributeError:
                    model.set(miter,
                              0,  key,
                              1, getattr(self.gui_fields[field_name], key, ''))
                
        try:
            cell = self.tvcolumns[field_name].get_cell_renderers()[0]
            model.set(model.append(), 0,  'width', 1, cell.get_data('width'))
        except:
            pass

        try:
            model.set(model.append(), 0,  'format', 1, self.gui_fields[field_name].format)
        except:
            pass

        dialog.show_all()
        response = dialog.run()
        dialog.destroy()
        
        
    def session_show(self, k=None):
        """just for debugging 
        """
        l = []
        j = 0
        for obj in self.session:
            if k is not None:
                print "%.2d %s %s" % (j, obj, hex(id(obj)))
            l += [(hex(id(obj)), obj)]
            j += 1

        l += [('dirty', self.session.dirty)]
        l += [('new', self.session.new)]
        l += [('delete', self.session.deleted)]
        if k is None:
            return l
        else:
            return l[k]
        
    def record_show_changes(self):
        if self.record_has_changed():
            for field in self.gui_fields:
                if field.has_changed():
                    print "OLD: %s   NEW: %s" % (field.initial_value, field.get_value())
                    
    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self.tables)

    def __str__(self):
        try:
            return '<%s: %s>' % (self.__class__.__name__, self.tables)
        except AttributeError, e:
            return '<%s>' % (self.__class__.__name__)




class UnsavedDataDialog(object):
    """
    A dialog that allows to see which data have been modifiedx
    """
    def __init__(self, master, type_="yes-no-cancel", msg=None, expanded=False):
        self.master = master
        general_msg = msg or _("Save unsaved data?")
        layout = "{v { i=gtk-dialog-question:6 l=msg}  {>%s.details TVS=details} }"

        self.dialog, l = master.lay_obj.dialog(title=_("Unsaved data"),
            type=type_, text=general_msg,  layout=layout %  (expanded and '>' or ''))

        tv = l.widgets['TV=details']
        expander = l.widgets['X.details']
        ## expanding the details will possibly trigget mask2obj that
        ## in turn will trogger validation. That's why I want to delay as much as possible
        self.model = gtk.TreeStore(str, str, str, str)
        if expanded:
            self.fill_model()
        else:
            expander.connect("notify::expanded", self.fill_model)
        
        tv.set_model(self.model)
        tv.set_property('width-request', 600)
        tv.set_property('height-request', 150)
        
        cell0 = gtk.CellRendererText()
        cell1 = gtk.CellRendererText()
        cell2 = gtk.CellRendererText()
        cell3 = gtk.CellRendererText()

        tc0 = gtk.TreeViewColumn(_("State"),     cell0, markup=0)
        tc1 = gtk.TreeViewColumn(_("Field name"), cell1, markup=1)
        tc2 = gtk.TreeViewColumn(_("Original value"), cell2, markup=2)
        tc3 = gtk.TreeViewColumn(_("Present value"), cell2, markup=3)

        tv.append_column(tc0)
        tv.append_column(tc1)
        tv.append_column(tc2)
        tv.append_column(tc3)
        tv.show_all()

        self.dialog.show_all()

    def run(self):
        response = self.dialog.run()
        self.dialog.destroy()
        return response

    def fill_model(self, *args):
        
        """
        Dialog to allow analysis of changed data
        """
        from sqlkit.db import utils 
        if self.master.is_mask():
            try:
                self.master.record_mask2obj(self.master.get_current_obj())
            except Exception, e:
                exc.ValidationError(e)

        if self.master.session.dirty or (
            self.master.record_has_changed() and self.master.current not in self.master.session.new):
            dirty_iter = self.model.append(None)
            self.model.set(dirty_iter, 0, '<b>%s</b>' % _('Modified'))

            for item in self.master.session.dirty:
                for field_name, old, new in utils.get_differences(item):
                    if item.__class__ is self.master.mapper.class_ and (
                        field_name in self.master.gui_fields):
                        
                        field = self.master.gui_fields[field_name]

                        old_value = old and utils.clean_for_markup(field.get_human_value(old)) 
                        new_value = new and utils.clean_for_markup(field.get_human_value(new)) 
                    else:
                        ## FIXME: we could also look for better representation in related widgets
                        old_value = utils.clean_for_markup(old)
                        new_value = utils.clean_for_markup(new)
                        
                    iter = self.model.append(None)
                    self.model.set(iter,
                                   0, "<i>%s</i>" % (utils.clean_for_markup(repr(item)[:25]) or
                                                     utils.clean_for_markup(item)[:25]),
                                   1, self.clearer("%s" % self.master.get_label(field_name)),
                                   2, self.clearer(old_value),
                                   3, self.clearer(new_value),
                                   )

        if self.master.session.deleted:
            deleted_iter = model.append(None)
            self.model.set(dirty_iter, 0, '<b>%s</b>' % _('Deleted'))
            for item in self.master.session.deleted:
                iter = self.model.append(None)
                self.model.set(iter,
                               0, "<i>%s</i>" % utils.clean_for_markup(item.__class__.__name__),
                               2, "%s" % utils.clean_for_markup(item))
                
                
        if self.master.session.new:
            new_iter = self.model.append(None)
            self.model.set(new_iter, 0, '<b>%s</b>' % _('New'))
            for item in self.master.session.new:
                iter = self.model.append(None)
                self.model.set(iter,
                               0, "<i>%s</i>" % utils.clean_for_markup(item.__class__.__name__),
                               3, "%s" % utils.clean_for_markup(item))
                
    def clearer(self, value):
        """
        return a string representation of '' vs. None so that user
        understands what is changing when just a 
        """
        from sqlkit.db import utils 
        if value == '':
            return utils.clean_for_markup('<%s>' % _("empty string: ''"))
        if value is None:
            return utils.clean_for_markup('<%s>' % _('NULL value'))
        return value


class ValidationErrorDialog(object):

    GENERAL_MSG = _('Errors are present in the record. \nCorrect them now, to continue \nor delete the record')
    TITLE = _("Validation errors")
    TYPE = 'ok'
    ERROR_DICT = 'validation_errors'
    IMAGE = 'gtk-dialog-error'
    
    def __init__(self, master):
        """
        represent the errors in self.validation_errors and raise ValidationError
        to correctly propagate the error upwards
        """
        self.master = master
        

        layout = """i=%s:6 l=general:<
                    TVS=details -""" % self.IMAGE
        
        self.dialog, lay = master.lay_obj.dialog(layout=layout, type=self.TYPE, title=self.TITLE)
        lay.widgets['l=general'].set_text(self.GENERAL_MSG)
        
        tv = lay.widgets['TV=details']
        model = gtk.ListStore(str, str)
        tv.set_model(model)
        tv.set_property('width-request', 420)
        tv.set_property('height-request', 150)
        
        cell1 = gtk.CellRendererText()
        cell2 = gtk.CellRendererText()

        tc1 = gtk.TreeViewColumn(_("Field name"), cell1, markup=0)
        tc2 = gtk.TreeViewColumn(_("Error"), cell2, markup=1)

        tv.append_column(tc1)
        tv.append_column(tc2)
        tv.show_all()
        self.error_dict = getattr(self.master, self.ERROR_DICT)
        self.fill_model(model)
        self.dialog.show_all()

    def run(self):
        response = self.dialog.run()
        self.dialog.destroy()

        self.error_dict = {}
        raise exc.DialogValidationError

    def fill_model(self, model):
        """
        Fill the model of the treeview that presents the validation errors
        """

        for key in self.error_dict.keys():
            for i, err in enumerate(self.error_dict[key]):
                iter = model.append(None)
                if i == 0:
                    model.set(iter, 0, "<b>%s</b>" % self.master.get_label(key))
                model.set(iter, 1, "<i>%s</i>" % err)
            

class ValidationWarningDialog(ValidationErrorDialog):

    GENERAL_MSG = _('You can continue or go back editing. \nRead the following warnings to decide')
    TITLE = _("Validation Warnings")
    TYPE = 'ok-cancel'
    ERROR_DICT = 'validation_warnings'
    IMAGE = 'gtk-dialog-warning'
    
    def run(self):
        response = self.dialog.run()
        self.dialog.destroy()

        self.error_dict = {}
        if response == gtk.RESPONSE_CANCEL:
            raise exc.DialogValidationError
        else:
            pass
