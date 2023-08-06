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
=========
Defaults
=========
"""
import datetime

import sqlalchemy

tables = {}
hooks = {}
layout_dict = {}
class_dict = {}

def set_default(table_name, tbl_dict):
    """
    Add a dictionary with one entry for each field of a table
    """
    global tables
    if table_name in tables:
        tdict = tables[table_name]
        tdict.update(tbl_dict)

    else:
        tables[table_name] = tbl_dict

class Defaults(object):

    def __init__(self, table_name, metadata=None, local=False):
        """
        :param table_name:  the name of the table for which we set default values 
        :param metadata: the metadata in which the table lives
        :param local: boolean: if the default is global (False) or local to a single widget
        """
        self.table_name = table_name
        self.metadata = metadata
        self.local = local
        if local:
            self.tdict = {}
        else:
            global tables
            if self.table_name in tables:
                self.tdict = tables[self.table_name]
            else:
                self.tdict = tables[self.table_name] = {}

    def set_defaults(self, tbl_dict):
        """
        set defaults using a dict as input
        :param tbl_dict: a dict of field_name:default_value. Default value can be a callable
        """
        self.tdict.update(tbl_dict)

    def set_default(self, **kw):
        """
        set a single default
        """
        for field_name, value in kw.iteritems():
            tbl_dict = {field_name: value}
            self.set_defaults(tbl_dict)

    def fk(self, field_name, attr, value):
        """
        Set a default and find at runtime (when setting default) which is the
        correct value (pk) based on attr and value
        
        :param field_name: the field_name for wich we set the default
        :param attr: the attribute to look for in the foreign table
        :param value: the value in the foreign key 
        """
        ## when we define defaults, metadata may not yet have loaded the table
        ## let's delay the moment...
        def get_by_description():
            from sqlkit.db.minspect import get_foreign_info
            from sqlalchemy.sql import select            

            global tables
            table = self.metadata.tables[self.table_name]
            col = table.columns.get(field_name)
            fkey = col.foreign_keys
            fk_table, fk_col = get_foreign_info(fkey, names=False)
            s = select([fk_col], getattr(fk_table.c, attr) == value)
            conn = self.metadata.bind.connect()
            result = conn.execute(s)
            row = result.fetchone()
            if row:
                #tables[self.table_name][field_name] = row[fk_col.name]
                self.tdict[field_name] = row[fk_col.name]
            else:
                #tables[self.table_name][field_name] = None
                self.tdict[field_name] = None
            return self.tdict[field_name]
        
        self.set_defaults( {field_name : get_by_description})
    
    today = datetime.date.today
    now = datetime.datetime.now


    def get(self, field_name):
        """
        Return the default value for a field_name
        if the value is a callable... call it
        """
        try:
            value = self.tdict[field_name]
            if callable(value):
                return value()
            else:
                return value

        except KeyError, e:
            return get_default(self.table_name, field_name)


def get_default(table_name, field_name):
    """
    Return the default value for a field_name
    if the value is a callable... call it

    :param table: the table for which we want defaults
    :param field_name: the name of the field 
    """
    if isinstance(table_name, sqlalchemy.Table):
        table_name = table_name.name
        
    try:
        value = tables[table_name][field_name]
    except KeyError, e:
        return

    if callable(value):
        return value()
    else:
        return value

def get_table_name(table):
    """
    return a table name. input may be a tablename or a sqlalchemy.Table
    """

    if isinstance(table, sqlalchemy.Table):
        table_name = table.name
    else:
        table_name = table

    return table_name

def register_hook(table, hook, nick='default'):
    """
    Register a hook for table. Each time a sqlwidget is instantiated for the table
    a hook is searched for here to initialize the sqlwidget

    :param table: a table for which we want to register the hook
    :param hook: the hook to be registered (a class or an instance)

    """
    from inspect import isclass

    global hooks
    
    if not isclass(hook):
        hook = hook.__class__
    
    table_name = get_table_name(table)
    hook_dict = hooks.get(table_name, {})
    hook_dict[nick] = hook
    hooks[table_name] = hook_dict

def unregister_hook(table, nick='default'):
    """
    unregister a hook

    :param table: the table or table_name for which you unregister the hook
    :param nick: the possible nick (default: 'default')
    """

    table_name = get_table_name(table)
    del hooks[table_name]

def unregister_layout(table, nick='default'):
    """
    unregister a layout 

    :param table: the table or table_name for which you unregister the layout
    :param nick: the possible nick (default: 'default')
    """

    table_name = get_table_name(table)
    del layout_dict[table_name]

def get_hook(table, instance=False, nick='default'):
    """
    Return a hook tor table or None

    :param table: the table for which we want the hook
    :param instance: a boolean: True is we want an instance False if we want the class
    """

    global hooks
    table_name = get_table_name(table)

    table_hooks = hooks.get(table_name, None)
    try:
        hook = table_hooks[nick]
    except (KeyError, TypeError), e:
        return None
    
    if instance:
        hook = hook()
    return hook

def register_layout(table, layout, nick='default', persistent=False):
    """
    Register a layout for table with a nick (default nick is 'default')
    Each time a sqlwidget is instantiated for the table
    a layout is searched for here 

    :param table: the table to register the layout for. May be a sqlakchemy.Table or a string
    :param layout: the layut to be registered
    :param nick: the name of a nick to use for this layout (used for SqlMask(... nick=nick)
    :param persistent: register in the _sqlkit tables (not yet implemented)
    """

    global layout_dict

    table_name = get_table_name(table)
    table_layout_dict = layout_dict.get(table_name, {})
    table_layout_dict[nick] = layout
    layout_dict[table_name] = table_layout_dict

    if persistent:
        raise NotImplementedError("registering of layout is not yet implemented")


def get_layout(table, nick='default'):
    """
    Return a layout for table for nick 'nick'

    :param table: the table to register the layout for. May be a sqlakchemy.Table or a string
    :param nick: the nick used for this layout 
    
    """
    
    global layout_dict
    table_name = get_table_name(table)

    table_layout_dict = layout_dict.get(table_name, None)
    try:
        return table_layout_dict[nick]
    except (KeyError, TypeError), e:
        return None

def register_class(class_, table=None, nick='default'):
    """
    Register a layout for table with a nick (default nick is 'default')
    Each time a sqlwidget is instantiated for the table
    a layout is searched for here 

    :param table: the table to register the layout for. May be a sqlakchemy.Table or
         a string. class_.__table__ is used as default
    :param layout: the layout to be registered
    :param nick: the nick
    """

    global class_dict

    if not table:
        table = class_.__table__
        
    table_name = get_table_name(table)
    table_class_dict = class_dict.get(table_name, {})
    table_class_dict[nick] = class_
    class_dict[table_name] = table_class_dict

def get_class(table, nick='default'):
    """
    Return a layout for table for nick 'nick'

    :param table: the table to register the layout for. May be a sqlakchemy.Table or a string
    :param nick: the nick used for this layout 
    
    """
    
    global class_dict
    table_name = get_table_name(table)

    table_class_dict = class_dict.get(table_name, None)
    try:
        return table_class_dict[nick]
    except (KeyError, TypeError), e:
        return None


