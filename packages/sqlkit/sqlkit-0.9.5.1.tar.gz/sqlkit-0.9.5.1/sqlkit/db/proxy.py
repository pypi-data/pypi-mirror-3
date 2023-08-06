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

from sqlalchemy import Table, MetaData, sql, __version__
from sqlalchemy.orm import sessionmaker, mapper
from sqlalchemy.orm.interfaces import SessionExtension
from pkg_resources import parse_version
try:
    from sqlalchemy import event
except ImportError:
    pass

from sqlkit import _
from sqlkit.db import minspect, utils
from sqlkit.exc import MissingPrimaryKey

class DbProxy(object):
    """
    A proxy to the database... it's meant to easy the way we pass information
    to the sqlwidget in the simpler situation:

    * if no metadata is passed, MetaData() will create it
    * if engine is passed it will be put in metadata as 'bind' attribute
    * if no session is passed a session is created via sessionmaker 

      db = proxy.DbProxy(engine='postgres://localhost/fossati')
      session = db.get_session()

    at that point sqlwidget will retrieve info this way::

      SqlTable(table="ticket_project", dbproxy=self.dbproxy)

    session defaults are: autoflush=False, autocommit=False

    """
    def __init__(self, metadata=None, engine=None, bind=None,
                 expire_on_commit=False,
                 Session=None, autocommit=True, autoflush=False):
        if metadata:
            self.metadata = metadata
        else:
            self.metadata = MetaData()
        if engine or bind:
            self.metadata.bind = engine or bind

        if not Session:
            try:
                self.Session = sessionmaker(bind=self.metadata.bind,
                                            expire_on_commit=expire_on_commit,
                                            autoflush=autoflush,
                                            autocommit=autocommit,
                                            )
                self.Session() # test if expire_on_commit is accepted
            except:
                self.Session = sessionmaker(bind=self.metadata.bind,
                                            autoflush=autoflush,
                                            autocommit=autocommit,
                                            )
        else:
            self.Session = Session
        self.engine = self.metadata.bind
            
    def get_session(self):
        sess = self.Session()
        if parse_version(__version__) < parse_version('0.7'):
            extension = SKSessionExtension()
            sess.extensions += [extension]
        else:
            emitter = Emitter()
            sess._sk_emitter = emitter
            event.listen(sess, 'after_flush', emitter.after_flush)
            event.listen(sess, 'after_flush_postexec', emitter.after_flush_postexec)
            event.listen(sess, 'after_commit', emitter.after_commit)
            
        return sess

    def get_table(self, name):
        """return a sqlalchemy.Table object from a table_name.
        Uses self.metadata"""
        
        if name in self.metadata.tables:
            return self.metadata.tables[name]
        else:
            return Table(name, self.metadata, autoload=True)

    
    def get_mapper(self, mapper_obj, tables):
        """If no mapper is provided it will be built from the table(s)
        tables may be:
           a list of table_names
           a list of sqlalchemy.Tables
           a single table_name
           a single sqlalchemy.Table
           a string of table_names
           when given as strings, table names will be joined automatically
           if a || sign is between 2 tables, outer join will be used, if nothing
           or | is used .join will be used.
        """
    
        from sqlalchemy.sql import Join

        if mapper_obj:
            return mapper_obj
    
        ## tables may be 'table1, table2, table3'
        if isinstance(tables, (Table, Join)):
            tables = [tables]
        elif not isinstance(tables, list):
            tables = re.sub("(\|\|?)", r" \1 ", tables)
            tables = re.split('[ ,]+', tables)
            tables = [self.get_table(tbl) for tbl  in tables]
            

        if len(tables) == 1:
            return table2mapper(tables[0])
        else:
            return self.join_tables(tables)

    def join_tables(self, tables, master=None):
        """
        join two or more tables in a mapper sqlalchemy.sql.Join

        tables can be string or sqlalchemy.Table object
        to force outer join || can be used, default is simple join (|)
        """
        class JoinAuto(object):
            pass

        j = None
        t1 = tables[0]
        mode = 'join'

        for t in tables[1:]:
            if t == '|':
                mode == 'join'
                continue
            elif t == '||':
                mode = 'outerjoin'
                continue
            
            if j:
                t1 = j
            j = self.join2tables(t1, t, mode=mode)

        m = mapper(JoinAuto, j)
        return m

    def join2tables(self, t1, t2, mode='outerjoin'):
        """return a join of 2 tables. Accept strings or sqlalchemy.Table"""
        tbl = {}
        ## 
        if isinstance(t1, str):
            T1_ret = True
            T1 = Table(t1, self.metadata, autoload=True)
        else:
            T1_ret = False
            T1 = t1
    
        if isinstance(t2, str):
            T2_ret = True
            T2 = Table(t2, self.metadata, autoload=True)
        else:
            T2_ret = False
            T2 = t2

        if mode == 'outer':
            return T1.outerjoin(T2)
        else:
            return T1.join(T2)


class Emitter(object):
    """Indirection component, needed to propagate session signals to widgets

    SQLA as of 0.7.2 doen not have a way to remove a listener, so an indirection
    layer is needed 
    """
    
    sk_widgets = None
    
    def after_flush(self, session, flush_context):
        """
        implement the after-flush signal
        """
        loop_run_hooks_over_widgets(self, session, 'on_after_flush', 'after-flush')
        
    def after_flush_postexec(self, session, flush_context):
        """
        implement the after-flush-postexec signal
        """
        loop_run_hooks_over_widgets(self, session, 'on_after_flush_postexec')
        
    def after_commit(self, session):
        """
        implement the after-commit hook
        """
        loop_run_hooks_over_widgets(self, session, 'on_after_commit', 'after-commit')
        
    def add(self, widget):
        "Add a sqlkit widget to the list of listenes"

        self.sk_widgets = self.sk_widgets or []
        self.sk_widgets += [widget]
        
    def remove(self, widget):
        "Add a sqlkit widget to the list of listenes"

        self.sk_widgets.remove(widget)
        

class SKSessionExtension(Emitter, SessionExtension):
    pass

def loop_run_hooks_over_widgets(ext, session, hook_name, signal_name=None):

    widgets = getattr(ext, 'sk_widgets', []) or []
    for sqlwidget in widgets:
        current= sqlwidget.get_current_obj()
        
        if sqlwidget:
            sqlwidget.run_hook(hook_name, current, session)
            if signal_name:
                sqlwidget.emit(signal_name, current, session)
        
        

def table2mapper(table):
    """
    return a mapper for a class created on the fly. table is a sqlalchemy.Table obj
    """

    X = get_default_class(table)
    if table.primary_key:
        m = mapper(X, table)
    else:
        primary_key = search_unique_keys(table)
        if primary_key:
            m = mapper(X, table, primary_key=primary_key)
        else:
            ## TIP: when assembling a mapper that does not have primary key
            msg = _("Table %s doesn't have a primary key, editing is not possible") % table.name
            raise MissingPrimaryKey(msg)
    return m

def get_default_class(table):
    """
    Create on the fly a proper class.
    utils.get_description() is used to set appropriate __str__ representation

    :param table: a sqlalchemy.Table object
    """
    name = "%s_class" % (table.name)
    format = utils.get_description(table, metadata=table.metadata, attr='format')

    def __str__(self):
        try:
            return format % vars(self)
        except KeyError:
            ## empt classe miss attributs...
            return "< %s: %s >" % (table.name.title(), hex(id(self)))

    def __repr__(self):
        return "< %s: %s >" % (table.name.title(), str(self))

    if isinstance(table, str ):
        table = self.get_table(name)

    name = name.encode('utf-8')
    X = type(name, (object,), {'__repr__' : __repr__, '__str__' : __str__})

    return X


def search_unique_keys(table):
    """
    return a column with unique index to be used if no other primary keys
    """
    
    for index in table.indexes:
        if index.unique:
            return index.columns

