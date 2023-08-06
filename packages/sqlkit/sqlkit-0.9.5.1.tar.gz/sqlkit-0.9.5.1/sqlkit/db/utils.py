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
.. _dbutils:

Utilities
=========

Hooks and Layout are the core for any customization. If you customize a
Mask, chances are you would like to use that customization, any time you open
that table, or you may need several different customization (eg. employees,
manager may share some fields and differ on other fields).

The following utilities give you the possibility to register Hooks and Layout
to make them available to any sqlwidget to which no Hook/Layout is passed.

Each time you register a hook/layout/class you can specify a nickname (eg.:
customer/provider)

Hooks
-----

.. autofunction::  register_hook

.. autofunction::  unregister_hook

.. autofunction::  get_hook

Layout
------

.. autofunction::  register_layout

.. autofunction::  unregister_layout

.. autofunction::  get_layout

Classes
-------

Classes can be registered as well. If you register a class, all the times you
pass a table to a sqlwidget, the class will be used, so that ll relations will
be available as well. This is particularly usefull in case you use
:ref:`RecordInMask` that can open a table that may use a layout with m2m/m2o
nested table that would result as unknown if the table was reflected from the
db.

.. autofunction::  register_class

.. autofunction::  get_class

Database
--------

.. autofunction::  get_differences


Descr
-----
This module provide a bare simple Class to help creating 
__str__ and __repr__ for tables, using _sqlkit_table.format field


tables
------

tables dictionary is a place where sqlkit looks for search_field and
format for tables (see: ref:`sqlkit_model`).

You can set values directly using TableDescr class or implicitely via
database editing (``sqledit -c url``)

.. _TableDescr:

Table Description
-----------------

.. autoclass:: sqlkit.db.utils.TableDescr
   :members: format, attrs, search, __init__


"""

import re

from sqlalchemy import Table, orm, select
from sqlalchemy.exc import OperationalError, ProgrammingError, InterfaceError

from defaults import register_hook, get_hook, register_layout, get_layout, register_class, \
     get_class, unregister_hook, unregister_layout

########   descriptor
from sqlkit.misc.utils import Container, DictLike, ObjLike

class MissingMetadata(Exception): pass

class Descr(object):
    """
    Simple class that provide default __init__ and __str__ to be
    mixed when building classes with declarative layer

    __str__ will use 'format' description from database _sqlkit_fields
    """
    def __init__(self, **kw):
        for key, val in kw.iteritems():
            setattr(self, key, val)
        if not hasattr(self, '__tablename__'):
            self.__tablename__ = self.__table__.name
    
    def __str__(self):
        from sqlkit.db.utils import tables

        if not hasattr(self, '__tablename__'):
            self.__tablename__ = self.__table__.name
    
        try:
            if not self.__tablename__ in tables:
                format = get_description(self.__table__, attr='format')

            return tables[self.__tablename__].format % DictLike(self)
        except:
            return "<%s - %s>" % (self.__class__.__name__, hex(id(self)))

    def __getitem__(self, key):
        return getattr(self, key) or ''

    __repr__ = __str__
    
class Tables(Container):
    def __getitem__(self, key):
        try:
            return getattr(self, key)
        except AttributeError:
            try:
                table = TableDescr(key, metadata=db.metadata)
                return table
            except Exception, e:
                raise MissingMetadata("No metadata defined in sqlkit.db.utils")
            

tables = Tables()

class TableDescr(object):
    """
    Handler for table search/format fields. This is an important component of
    :ref:`completion` as it determines:


    1. what is searched for (`search` attribute)
    2. how it will be represented (`format` attribute)

    TableDescr is automatically built from within :func:`get_description`. 
    In __init__ it queries the database' sqlkit_table to see if any site-wide
    configuration is available.

    In turn :func:`get_description` is called within completion classes and
    :meth:`sqlkit.fields.ForeignKeyField.lookup_value`
    
    """

    format = None
    """The format string used to represent the record.

    When no format string is passed to the constructor, the first string
    field of the table is used. That clearly may be totally wrong in some
    cases, that's why you can change it.

    May be eather a normal python format string
    (eg.: "%(title)s - %(year)s")
    in which case each prenthesized token must be a *field_name*
    or a simple string that again must be a *field_name* (e.g.: ``last_name``)
    The representation of a director as in our demo could be:
    ``%(first_name)s %(last_name)s`` 

    Format string passed to TableDescr take precedence over format string
    present in the database. 
    """
    
    attrs = None
    """List of attributes required by the format string.  Always includes
    pkey."""
    
    search = None
    """this is the field that will be searched for in a foreign key.
    When using completion in a ForeignKey the database is queried using this field as a filter.
    E.g.: if in a SqlMask for a Movie you enter ``fe`` and then complete (Control-Enter) a
    query is build on the fly and sent to the database that selects the director's table with
    an additional ``"SELECT DISTINCT %(attrs) FROM director WHERE %s = 'fe'" % (attrs, search_field)``.

    It has the same default as :attr:`format` above.
    """
    # FIXME: here description is an alias for search_field, in completion
    # description is an alias for format_field...
    pattern = '%\((\w+)\)'
    def __init__(self, table, format=None, pk=None, metadata=None, register=True):
        """
        Handler for table search/format fields

        :param table: the table_name or the sqlalchemy Table
        :param format: a possible format string, used to represent the record.
            See :attr:`format` above.

        :param pk: suggests which pk are to be used
        :param metadata: necessary to pick primary key or when autoloading is
                   required unless a Table object is given
        :param register: (boolean) if True (default) this Table Description will be
                   registered as default


        """
        if register:
            global tables
        else:
            tables = {}

        if isinstance(table, Table):
            self.table = table
            table_name = table.name

        elif isinstance(table, basestring):
            table_name = table

        elif hasattr(table, 'original'):  # A Table.alias()
            self.table = table.original
            table_name = table.original.name

        self.table_name = table_name
        self.metadata = metadata
        
        tables[table_name] = self

        self.description, dbformat = self.guess_description()

        if format:
            self.set_format(format)
        elif dbformat:
            self.set_format(dbformat)
        else:
            self.set_format(self.description)

        ## I want self attr to have pkey, that's handy for completion
        if not pk:
            self.add_pk()
        else:
            if pk not in self.attrs:
                self.attrs.insert(0, pk)

    def get_attrs_from_format(self, format):
        """
        Used when format is 
        """
        m = re.findall(self.pattern, format)
        if m:
            return m
        else:
            return [format]
        
    def set_format(self, format):
        m = re.findall(self.pattern, format)
        ## self.attrs is use to get the minimum possible info when completing
        if m:
            self.attrs = m
            self.format = format
        else:
            self.attrs = [format]
            self.format = "%%(%s)s" % format
            self.search = format

    def add_pk(self):

        table = self.get_table()
        pkeys = table.primary_key.columns

        for field in pkeys:
            if field.name not in self.attrs:
                self.attrs.insert(0, field.name)
                
    def get_table(self):
        """
        return the sqlalchemy.Table or try to get it from metadata
        """

        try:
            return self.table
        except AttributeError:
            if not self.metadata:
                raise MissingMetadata("Description  for '%s' cannot be guessed" % self.table_name)
        
        ## first time we meet this table  -> inspect w/ autoload
        return Table(self.table_name, self.metadata, autoload=True)

    def guess_description(self):
        """look if a description (format) field is defined, if not use introspection
        return the description

        """
        table = self.get_table()
        description, format = get_description_from_sqlkit(table)
        if description:
            return description, format

        for field_name in table.c.keys():
            if re.search("string|text|char", table.c[field_name].type.__class__.__name__, re.I):
                break

        return field_name, format
        
    def __str__(self):
        return "table: %s - description: %s\n    format: %s" % (self.table_name, self.description,
                                                            self.format)

    def __repr__(self):
        return "table: %s - format: %s" % (self.table_name, self.format)


def get_table_name(table):
    if isinstance(table, Table):
        table_name = table.name
                
    elif isinstance(table, basestring):
        table_name = table

    elif hasattr(table, 'original'):  # A Table.alias()
        table_name = table.original.name
        
    return table_name

def get_description(table, metadata=None, attr='attrs'):
    """
    return info on table according to data already available
    or guessing by introspection of the table

    :param table: the sa table or table_name for which we search the description
    :returns: 'attrs' or what defined by 'attr' keywrord arg
    """

    table_name = get_table_name(table)

    try:
        return getattr(tables[table_name], attr)
    except MissingMetadata, e:
        if isinstance(table, Table):
            return getattr(TableDescr(table), attr)
        return getattr(TableDescr(table_name, metadata=metadata), attr)
    
def get_description_from_sqlkit(table, metadata=None):
    """
    get the description to use in completion and __str__ from database
    table _sqlkit_table
    
    :param table: the sa table or table_name for which we search the description
    :returns: a tuple (search_field, format) that may be (None, None)
    """
    if isinstance(table, Table):
        metadata = table.metadata

    from sqlkit.db.sqlkit_model import get_classes
    table_class, field_class = get_classes(metadata.bind)

    if not metadata.bind.has_table(table_class.__tablename__):
        return None, None

    try:
        tbl = table_class.__table__
        sql = select([tbl.c.search_field, tbl.c.format], tbl.c.name == table.name)
        res_proxy = metadata.bind.execute(sql)
        descr = res_proxy.fetchone()
        if not descr:
            descr = None, None
    except (OperationalError, ProgrammingError), e:  #_sqlkit_table is not defined
        descr = (None, None)
    return descr

def get_labels_and_tips_from_sqlkit(table, metadata=None):
    """
    get the labels and tips to use in label_map from
    table _sqlkit_field
    """
    if isinstance(table, Table):
        metadata = table.metadata
        table_name = table.name
    else:
        table_name = table
        
    from sqlkit.db.sqlkit_model import get_classes
    table_class, field_class = get_classes(metadata.bind)

    if not metadata.bind.has_table(field_class.__tablename__):
        return {}

    descr = {}
    try:
        tbl = field_class.__table__
        sql = select([tbl.c.table_name, tbl.c.name, tbl.c.description, tbl.c.help_text],
                     tbl.c.table_name == table_name)
        res_proxy = metadata.bind.execute(sql)
        for record in res_proxy.fetchall():
            descr[record.name] = (record.description, record.help_text)
    except (OperationalError, ProgrammingError), e:
        #_sqlkit_field is not defined
        pass
    return descr

###################


def get_differences(obj):
    """
    show differences between old and new version of an object
    this is a generator, you should use as in::

       for field_name, old_value, new_value in get_differences(obj):
           print 'field   %s changed from %s, to %s' % (field_name, old_value, new_value)

    :param obj: the object to look for changes

    this function uses ``sqlalchemy.orm.attributes.get_history`` but differs in 2 ways:

      * it only yield *changed* values
      * it returns the simple value (not a list) if the property is not a RelationProperty
        with direction MANYTOMANY or ONETOMANY (i.e.a collection)
    
    """

    session = orm.object_session(obj)
    mapper = orm.class_mapper(obj.__class__)
    for prop in mapper.iterate_properties:
        new = None
        old = None

        try:
            new, unchanged, old =  orm.attributes.get_history(obj, prop.key)
        except AttributeError, e:
            # sqla 0.5.0 -> 0.5.1
            new, unchanged, old =  orm.attributes.get_history(
                orm.attributes.instance_state(obj), prop.key)
        if new or old:
            ## Not sure about this code. I don't want to have to cope with
            ## a list if there is no need for that (i.e. is not a collection)
            if isinstance(prop, orm.properties.RelationProperty) and (
                prop.direction.name in ('MANYTOMANY', 'ONETOMANY')):
                yield prop.key, old, new
            else:
                try:
                    old = old[0]
                except (TypeError, IndexError):
                    old = None
                    
                try:
                    new = new[0]
                except (TypeError, IndexError):
                    new = None
                    
                yield prop.key, old, new

def get_history(obj, field_name, session=None):
    """
    show the history of a field of an object

    :param obj: the object to look for history
    :param field_name: the field name of which we want to know the history
    :return: new, unchanged, old
    """

    mapper = orm.class_mapper(obj.__class__)
    for prop in mapper.iterate_properties:

        if prop.key == field_name:

            try:
                try:
                    new, unchanged, old =  orm.attributes.get_history(obj, prop.key)
                except AttributeError, e:
                    # sqla 0.5.0 -> 0.5.1
                    new, unchanged, old =  orm.attributes.get_history(
                        orm.attributes.instance_state(obj), prop.key)
                if isinstance(prop, orm.properties.RelationProperty) and (
                    prop.direction.name in ('MANYTOMANY', 'ONETOMANY')):
                    return new, unchanged, old
                else:
                    return new and new[0] or '',  unchanged and unchanged[0] or '', old and old[0] or ''

            except Exception, e:
                pass
            
def clean_for_markup(text):
    """
    quote string from undesired chars in pango markup
    """
    from gobject import markup_escape_text
    
    if isinstance(text, (tuple, list)):
        text = [markup_escape_text(str(item)) for item in text]
    else:
        text = markup_escape_text(str(text))
    return str(text)


def get_fields(table, metadata=None, name=True):
    """
    return all field_names for this table
    table may be a sqlalchemy.Table or a table_name in which case a metadata
    must be provided as well.

    If a registered class is found, all properties are returned, i.e. also
    relation properties (PropertyLoaders). This may change...?
    """
    # first try if a registered class exists
    class_ = get_class(table)

    if class_:
        mapper = orm.class_mapper(class_)
        if name:
            return mapper.c.keys()
        else:
            return [c for c in mapper.c]
    else:
        if not isinstance(table, Table):
            if not metadata:
                raise MissingMetadata("A metadata must be provided as autoload is needed")
            try:
                table = Table(table, metadata, autoload=True)
            except Exception, e:
                e.message = "Missing table: %s" % table
                raise e
        if name:
            return table.c.keys()
        else:
            return [c for c in table.c]


if __name__ == '__main__':
    from sqlkit.db import proxy

    db = proxy.DbProxy(engine="sqlite://///misc/src/hg/py/sqlkit4/doc/db/movies.sqlite")
    movie = Table('movie', metadata=db.metadata, autoload=True)

    #t = TableDescr('movie', '%(dirctor_id)s - (%(nation)s)', metadata=db.metadata)

    tables['movie'].attrs
    print get_description(movie, attr='format')
    print tables.movie
    print get_description('movie', metadata=db.metadata)
    print get_description('movie', metadata=db.metadata, attr='format')    


