# Copyright (C) 2008-2010, Sandro Dentella <sandro@e-den.it>
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

import gtk
import sqlalchemy as sa

import sqlkit
from sqlkit import debug as dbg, _, fields
from sqlkit.widgets import SqlTable, SqlMask
from sqlkit import layout
from sqlkit.db import utils

GENERAL_UI = '''
  <menubar name="Main">
     <menu action="Database">
        <menuitem action="EditFields"/>
        <separator name="sep1"/>
        <menuitem action="Quit"/>
     </menu>
     <menu action="Modify">
        <menuitem action="Reload"/> 
        <menuitem action="Dev"/>
        <menuitem action="Blank"/>
    </menu>

    <menu action="Tools">
        <menuitem action="Count" />
    </menu>

     <menu action="Help">
        <menuitem action="About"/>
     </menu>
     

  </menubar>
  <toolbar name="TbMain">
    <toolitem  action="Quit" />
    <toolitem  action="Reload" />
    <toolitem  action="Blank" />
    <toolitem  action="Dev" />
  </toolbar>
'''

class TableBrowser(object):

    NAME_COLUMN = 0
    COUNT_COLUMN = 1
    TYPE_COLUMN = 2
    DEFAULT_COLUMN = 3
    PKEY_COLUMN = 4
    FKEY_COLUMN = 5
    NULL_COLUMN = 6
    INDEX_COLUMN = 7
    COUNT_VISIBILITY_COLUMN = 8
    
    
    def __init__(self, dbproxy, title=None, opts=None, x=None):
        
        lay = """
             {V.menu }
             {- b=filter_tables e=filter}
             prg=count
             TVS=tree

        """
        self.tables = {}
        self.x = x
        if opts:
            self.opts = opts
        else:
            class Opts: pass
            opts = Opts()
            opts.load = True
            opts.dev = False
            opts.all_tables = None
            self.opts = opts
            
        self.dbproxy = dbproxy
        self.l = layout.Layout(lay, title=title, opts='-')
        self.l.pack(
            ## fill is just to avoid default that is expand
            ('T.0',             'y-options', 'fill'),
            ('b=filter_tables', 'x-options', 'fill'),
            )
        self.model = gtk.TreeStore(*[str] + [int] + [str] * 6 + [bool] )
        self.w = self.l.show()
        self.w['prg=count'].hide()
        self.tv = self.w['TV=tree']
        cols = ['Table', 'N.rows', 'Type', 'Default', 'Prim. Key',
                'Foreign Key', 'Nullable', 'Indexes']
                
#         cols = [_('Table'), _('N. rows'), _('Default'), _('Prim. Key'), _('Foreign Key'),
#                 _('Nullable'), _('Indexes')]
        self.stv = layout.misc.EasyTreeView(cols, model=self.model, tv=self.tv)
        count_column = self.stv.tvc['N.rows']
        count_cell = count_column.get_cell_renderers()[0]
        count_cell.set_property('xalign', 1.0)
        count_column.add_attribute(count_cell, 'visible', self.COUNT_VISIBILITY_COLUMN)

        self.tv.connect('button-press-event', self.popup_col_menu)
        self.l.connect(
            ('b=filter_tables', 'clicked', self.fill_model),
            ('e=filter', 'activate', self.fill_model),
            ('Window', 'delete-event', self.quit_cb),
            )
        self.fill_model()
        self.lay_obj = self.l
        self.widgets = self.w
        self.set_actions()
        self.prepare_uimanager()
        self.add_accelerators()
        self.ui_manager.get_action('/Main/Modify/Blank').set_active(not fields.BLANK_OK)

        from sqlkit.widgets.table.utils import set_height_request
        set_height_request(self.tv, rows=min(30, len(self.model)))
        self.ui_manager.get_action('/Main/Modify/Reload').set_active(bool(opts.load))   

    def set_actions(self):
        self.actiongroup  = gtk.ActionGroup('Main')
        self.actiongroup.add_actions([
            ('Database', None, _('Database')),
            ('Modify', None, _('Modify')),
            ('Tools', None, _('Tool')),
            ('Help', None, _('Help')),
            ('Quit', gtk.STOCK_QUIT, None, '<Ctrl>q', None, self.quit_cb),
            ('About', gtk.STOCK_ABOUT, None, None, None, self.about_dialog_cb),
            ('Count', None, _('Count records'), None, _('Count records in all tables'),
             self.count_records),
            ])
        tooltip = _("""Configure the fields: \nlabels, tooltip, completion, search field""")

        self.actiongroup.add_actions([
            ('EditFields', None, _('Edit Sqlkit Fields'), '<Ctrl>e', tooltip, sqlkit_model),
            ], self.dbproxy)
        self.actiongroup.add_toggle_actions([
            ('Dev', 'sk-pkeys', _('Primary Key'), None,
             _('Show/Hide primary key if the key is numeric'), self.toggle_dev_cb),
            ('Reload', 'sk-table-load', _('Load data'), None,
             _('Load the data as well'), self.toggle_reload_cb),
            ('Blank', 'gtk-bold', _('Blank'), None, _('Cast blank into NULL'), self.toggle_blank_cb),
            ])

    def toggle_reload_cb(self, item):
        pass

    def toggle_dev_cb(self, item):
        pass
            
    def toggle_blank_cb(self, item):

        fields.BLANK_OK = not self.ui_manager.get_action('/Main/Modify/Blank').get_active()
            
    def prepare_uimanager(self):

        self.ui_manager = gtk.UIManager()
        self.accel_group = self.ui_manager.get_accel_group()
        self.ui_manager.add_ui_from_string(GENERAL_UI)
        self.w['Window'].add_accel_group(self.accel_group)
        self.ui_manager.insert_action_group(self.actiongroup, 0)
        header = self.w['V.menu']
        menu    = self.ui_manager.get_widget('/Main')
        tools    = self.ui_manager.get_widget('/TbMain')
        header.add(menu)
        header.add(tools)
        
    def count_records(self, item):
        """
        Count the records in all tables
        """
        progress = self.widgets['prg=count']
        progress.show()
        
        n_tables = len(self.model)
        sess = self.dbproxy.get_session()
        meta = self.dbproxy.metadata

        i = 0
        for row in self.model:
            if not self.model.get(row.iter, self.COUNT_COLUMN)[0]:
                table_name = self.model.get(row.iter, 0)[0]
                i += 1
                progress.props.text = table_name
                progress.props.fraction = (1.0/n_tables * i)
                while gtk.events_pending():
                    gtk.main_iteration()
                reflected_table = meta.tables.get(table_name, None)

                if reflected_table is None:
                    reflected_table = sa.Table(table_name, meta, autoload=True)

                count = sess.query(reflected_table).count()
                self.model.set(row.iter,
                               self.COUNT_COLUMN, count,
                               self.COUNT_VISIBILITY_COLUMN, True
                               )
        progress.props.fraction = 1.0
        progress.hide()


    def add_accelerators(self):
        """Add accelerators: now Ctrl-l"""

        # key accelerators
        self.accel_group.connect_group(ord('l'), 
                                       gtk.gdk.CONTROL_MASK, 
                                       gtk.ACCEL_LOCKED, 
                                       self.focus_filter)
        self.accel_group.connect_group(ord('f'), 
                                       gtk.gdk.CONTROL_MASK, 
                                       gtk.ACCEL_LOCKED, 
                                       self.focus_filter)
            
    def focus_filter(self, *args):
        self.widgets['e=filter'].grab_focus()

    def quit_cb(self, widget, event=None):
        if self.x == 'quit':
            gtk.main_quit()
        else:
            self.widgets['Window'].destroy()
            
    def reload(self, *args):
        dbg.write('reloading sqlkit')
        #print reload(sqlkit)
        #reload(sqlkit.sqlwidget)
        #print reload(sqlkit.table.table)
        #reload(sqlkit.mask.mask)
        
    def popup_col_menu(self, wdg, ev ):
        try:
            self.w['M=popup'].destroy()
        except:
            pass
        iter = self.model.get_iter(
            wdg.get_path_at_pos(int(ev.x),int(ev.y))[0])
        if self.model.iter_parent(iter):
            return 
        table = self.model.get_value(iter,0)
        
        if  self.model.iter_has_child(iter) and \
               self.tv.row_expanded(self.model.get_path(iter)):
            return False
        #table = self.model.get_value(self.model.get_iter(path), 0)

        
        menu = self.w['M=popup'] = gtk.Menu()

        item = gtk.MenuItem(label=_("Mask") )
        item.connect('activate', self.activate_cb, ('mask', table ))
        menu.append(item)

        item = gtk.MenuItem(label=_("Table") )
        item.connect('activate', self.activate_cb, ('table', table ))
        menu.append(item)

        if self.model.iter_children(iter) and \
               self.tv.row_expanded(self.model.get_path(iter)):
            item = gtk.MenuItem(label=_("Collapse row") )
            item.connect('activate', self.get_table_info_in_model, table, iter )
            menu.append(item)
        else:
            item = gtk.MenuItem(label=_("Table reflection") )
            item.connect('activate', self.get_table_info_in_model, table, iter )
            menu.append(item)

        menu.show_all()
        menu.popup(None, None, None, ev.button, ev.time)
        return False

    def activate_cb(self, wdg, data):

        mode, table = data
        dev = self.ui_manager.get_action('/Main/Modify/Dev').get_active()
        options ={
               'dev' : dev,
               'single' : False,
               'nick' : "%s_%s" % (table, mode),
               'dbproxy' : self.dbproxy,
           }
        if mode == 'mask':
            SqlWid = SqlMask
        else:
            SqlWid = SqlTable

        try:
            self.t = SqlWid(table, **options)
            if self.ui_manager.get_action('/Main/Modify/Reload').get_active():
                self.t.reload()
        except sqlkit.exc.MissingDescriptorField:
            pass
        except sqlkit.exc.MissingPrimaryKey, e:
            dialog, l = self.l.dialog(type='ok', layout="l=msg", text=e)
            dialog.show_all()
            response = dialog.run()
            dialog.destroy()
    
    def skip_table(self, table):
        """ this is just for skipping, must return True"""
        
        if self.dbproxy.metadata.bind.name == 'postgres' and table.startswith('pg_'):
            return True
        if not re.search(TABLE_MATCH, table):
            return True

    def fill_model(self, *args):
        """
        called by button filter_table and filter entry
        """
        global TABLE_MATCH
        self.model.clear()
        TABLE_MATCH = self.w['e=filter'].get_text() or ".*"
        tables = self.dbproxy.metadata.bind.table_names()
        tables.sort()
        for table in tables:
            if self.skip_table(table):
                continue
            iter = self.model.append(None)
            self.model.set(iter, self.NAME_COLUMN, table)
            if self.opts.all_tables:
                self.get_table_info_in_model(None, (table, iter))

    def get_table_info_in_model(self, junk, table_name, iter):
        """
        fill the model relative to info on table 
        """
        if  self.model.iter_has_child(iter):
            if self.tv.row_expanded(self.model.get_path(iter)):
                self.tv.collapse_row(self.model.get_path(iter))
            else:
                self.tv.expand_row(self.model.get_path(iter), True)
            return False
        
        tbl = sa.Table(table_name, self.dbproxy.metadata, autoload=True)
        index_dict = {}
        self.tables[table_name] = tbl
        pks = []
        for pk in tbl.primary_key:
            pks += [pk.name]

        ## Indexes
        for i, index in enumerate(tbl.indexes):
            for j, col in enumerate(index.columns):
                # show order of column in index
                if not col.name in index_dict:
                    index_dict[col.name] = []
                index_dict[col.name] += [index.unique and 'UNIQUE_%s.%s' % (i, j)
                                         or 'IDX_%s.%s' % (i,j)]

        ## pkey and count visibility
        self.model.set(iter,
                       self.PKEY_COLUMN,               ",".join(pks),
                       self.COUNT_VISIBILITY_COLUMN,   False, 
                       )
            
        ## loop on columns
        for c in tbl.c:
            iter2 = self.model.append(iter)
            self.model.set(iter2, self.NAME_COLUMN, c.name )
            self.model.set(iter2, self.TYPE_COLUMN, c.type.compile(
                dialect=tbl.metadata.bind.engine.dialect))
            if c.primary_key:
                self.model.set(iter2, self.PKEY_COLUMN, 'X' )
            if c.foreign_keys:
                self.model.set(iter2, self.FKEY_COLUMN,
                               ",".join([x.target_fullname for x in c.foreign_keys]) )
            if not c.nullable:
                self.model.set(iter2, self.NULL_COLUMN, "NOT NULL")
            if c.name in index_dict:
                self.model.set(iter2, self.INDEX_COLUMN, " ".join(index_dict[c.name]))
            
        path = self.model.get_path(iter)
        self.tv.expand_row(path, True)
                

        
    def about_dialog_cb(self, menuItem):
        """
        The about dialog
        """
        dialog = create_about_dialog()
        dialog.run()
        dialog.destroy()
        

def sqlkit_model(item=None, dbproxy=None, single=False):
    lay = """
       name
       search_field
       format
       o2m=attributes -

    """
    global tbl
    if dbproxy:
        db = dbproxy
    try:
        from sqlkit.db.sqlkit_model import get_classes, Base
        SqlkitTable, SqlkitFields = get_classes(db.metadata.bind)
        Base.metadata.bind = db.metadata.bind
        if not db.metadata.bind.has_table('_sqlkit_table'):
            response = dialog_create_continue()
            if response == gtk.RESPONSE_CANCEL:
                sys.exit(0)
            else:    
                Base.metadata.create_all()
                
        tbl = SqlMask(SqlkitTable, dbproxy=db, single=single,
                      hooks=ConfigHook(), layout=lay)
        tbl.widgets['l=name'].set_tooltip_text(_('The name of the table we are customizing'))
        format_tip = _("The best representation of a record \nas a combination of fields, " +\
                       "e.g.: %(title)s %(year)s")
        tbl.widgets['l=format'].set_tooltip_text(format_tip)
        search_tip = _('The field that will be searched for when completion is used')
        tbl.widgets['l=search_field'].set_tooltip_text(search_tip)
    except Exception, e:
        print e
        raise

def dialog_create_continue():
    dialog = gtk.Dialog("Creating sqlkit tables", None,
                        gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                        (gtk.STOCK_OK, gtk.RESPONSE_OK,
                         gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
    label = gtk.Label("No sqlkit tables are present: I'll proceed creating them")
    dialog.vbox.add(label)
    dialog.show_all()
    response = dialog.run()
    dialog.destroy()
    return response


def create_about_dialog():
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

def open_sqlwidget(table, single, opts, db):

    options ={'dev' : opts.dev,
              'single' : single,
              'limit' : opts.limit and int(opts.limit) or 200,
              'dbproxy' : db,
              'sql' : opts.sql,
              'field_list' : opts.field_list,
              'order_by' : opts.order_by,
           }
    if opts.mask:
        try:
            t = SqlMask(table, **options)
        except sqlkit.exc.MissingDescriptorField:
            pass

    else:
        try:
            t = SqlTable(table, **options)
        except sqlkit.exc.MissingDescriptorField:
            pass

    if opts.load:
        t.reload()
    return t

class ConfigHook(object):

    def on_init(self, m):
        self.m = m
        self.db = m.dbproxy
        m.completions.name.set_values(self.db.metadata.bind.table_names())
        m.completions.name.autostart = 1

        
        m.completions.search_field.set_values(self.get_names)
        m.completions.search_field.autostart = 1
        m.related.attributes.completions.name.set_values(self.get_all_names)
        m.related.attributes.completions.name.autostart = 1

    def get_names(self, values = None):
        table = self.m.get_value('name')
        if table:
            cols = utils.get_fields(table, metadata=self.db.metadata, name=False)
            return [c.name for c in cols if isinstance(c.type, (sa.String, sa.Text))]
        else:
            return []

    def get_all_names(self, values = None):
        table = self.m.get_value('name')
        if table:
            return utils.get_fields(table, metadata=self.db.metadata, name=True)
        else:
            return []



