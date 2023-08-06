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

"""
Django syntax utilities
=======================

This module provides some functions to allow use of django syntax in filters.
You can look an introduction on lookup filters on `django's site`_ but mind that
we don't even share the same syntax. We just borrowed the idea that the operator
and possibly the join can be wired in the keyword *name*.
The aim is not at all compatibility with django (that has nothing to do with this
framework) but a way to:

  * make it easy to add filters and constraints
  * make it easy to store queries (that need to store filters and constraints)

These function are used in sqlfilter and in completion beside ``.add_constraint(...)``
method of sqlwidget. 

You never *need* to use these functions. If you prefere you can changed the query
directly with SQLAlchemy syntax, and surely there are situations where that's
necesssary, nevertheless there are situations where this syntax allows to obtain the
same result in less and more readeable code, probably just one line.

All of these functions act on a mapper becouse it has info on PropertyLoaders. In completion,
the mapper is used to follow the *join_path* even if the query (a ``sqlalchemy.select``),
will not be issued on a ``session.query`` object

.. _`django's site`: http://docs.djangoproject.com/en/dev/topics/db/queries/#field-lookups-intro

supported lookup
----------------

:like/ilike:        use like operator, ilike if available
:notlike/notilike:  negate like operator, ilike if available
:regexp/iregexp:    now ~/~* for postgres and REGEX for mysql like again for the rest
:notregexp/notiregexp:    now !~/!~* (only for postgresql)
:lt/gt:             less than / grater than (<, >)
:lte/gte:           less than equal/ grater than equal(<=, >=)
:eq/neq:            equal / not equal ( = , !=)
:in/notin:          IN (argument must be a list)/ negated
:null:              IS NULL / IS NOT NULL (depending if arg is True/False)
:emptynull:         IS NULL or EMPTY

conjunctions
------------

:func:`django2sqlalchemy` and :func:`django2query` connect all arguments with AND operator
by default. It's possible to use ``OR`` operator adding ``OR=True``  argument.

.. autofunction:: django2sqlalchemy

.. autofunction:: django2query


"""
from copy import deepcopy

from sqlalchemy.sql.expression import ColumnElement, ClauseList 
from sqlalchemy.sql import and_, or_, not_
from sqlalchemy import Table
from sqlalchemy.orm import ColumnProperty, PropertyLoader, class_mapper
from sqlalchemy.types import Date, DateTime

from sqlkit.misc.datetools import string2dates
from sqlkit.db import utils

OPERATORS = {
    'icontains'  : 'icontains',
    'notlike'    : 'not like',
    'like'       : 'like',
    'ilike'      : 'ilike',
    'notilike'   : 'not ilike',
    'iregexp'    : '~*',
    'regexp'     : '~',
    'notiregexp' : '!~*',
    'notregexp'  : '!~',
    'lt'         : '<',
    'gt'         :  '>',
    'lte'        : '<=',
    'gte'        : '>=',
    'eq'         : '=',
    'neq'        : '!=',
    'equal'      : '=',
    'in'         : 'IN',
    'notin'      : 'NOT IN',
    'null'       : 'IS NULL',
    'notnull'    : 'IS NOT NULL',
    'emptynull'    : 'EMPTY OR NULL',
    }

class DjangoParser(object):
    """
    Parser for django-like syntax.
    
    Parses a django-like argument to compose a sqlalchemy
    ColumnList/ColumnElement object to be used in queries
    """
    def __init__(self, mapper_or_table=None, query=None, OR=False, aliased=False, outer=False):
        """
        A sqlalchemy.Table object

        :param mapper_or_table: the mapper or table to be parsed
        :param query: the query that will be use as base
        :param OR: (boolean) it True all conditions will be ORed
        :param aliased: (Boolean) passed to join conditions if any
        :param outer: the join will be an OUTER JOIN
        """
        self.aliased = aliased
        self.outer = outer
        if isinstance(mapper_or_table, Table):
            self.mapper = None
            self.table = mapper_or_table
            class_ = utils.get_class(self.table.name)
            if class_:
                self.mapper = class_mapper(class_)
                                     
        else:
            self.mapper = mapper_or_table
            self.table = self.mapper.local_table

        self.query = query
        self.OR = OR
        self.expressions = []
        self.joins = []

    def parse(self, kw):
        """
        must be a single condition
        parse a django-like condition
        """
        if self.mapper:
            join_path, op, op_str, value, col, join_args = django2components(self.mapper, kw=kw)
        else:
            join_path, op, op_str, value, col, join_args = django2components(self.table, kw=kw)
            
        self.joins += [join_path]

        if op_str == 'icontains':
            eng_name = self.table.metadata.bind.name
            if eng_name.startswith('postgres'):
                sql = col.op('~*')(value)
            elif eng_name.startswith('mysql'):
                sql = col.op('REGEXP')(value)
            else:
                sql = col.ilike("%%%s%%" % value.strip('%'))
                
        elif op_str == 'null':
            sql = col == value  ## True | False
        elif op_str == 'ilike': # SA manages difference where there is no ILIKE operator
            sql = col.ilike(value)
        elif op_str == 'notilike': # SA manages difference where there is no ILIKE operator
            sql = not_(col.ilike(value))
        elif op_str == 'in': 
            sql = col.in_(value)
        elif op_str == 'notin': 
            sql = not_(col.in_(value))
        elif self.is_date(col):
            if isinstance(value, basestring):
                start, stop = string2dates(value)
            else:
                start, stop = value, None
            if stop:
                sql = col.op('>=')(start)  &  col.op('<=')(stop)
            else:
                sql = col.op(op)(start)
        else:
            sql = col.op(op)(value)

        self.expressions += [sql]
            
    def is_date(self, col):

        if isinstance(col.type, (Date, DateTime)):
            return True
        return False
        
    def sql(self):
        if self.OR:
            sql = or_(*self.expressions)
        else:
            sql = and_(*self.expressions)
        return sql

    def compose(self):
        for path in self.joins:
            if path:
                if self.outer:
                    self.query = self.query.outerjoin(aliased=self.aliased, *path).reset_joinpoint()
                else:
                    self.query = self.query.join(aliased=self.aliased, *path).reset_joinpoint()

        return self.query.filter(self.sql() )

#######  Functions  ############
    
def django2components(mapper_or_table, kw=None):
    """
    Split a single argument/value into a tuple of 5 components:

      :path:    what should be used in a join to reach the column of the expression
      :op:      simbolic version of the operator (eg: <=)
      :str_op:  string version of the operator (eg: lte)
      :value:   value of the argument
      :col:     sqlalchemy column on which the expression will operate 
      :join_args: args for a query.join. At present is only returned for first_step joins and is
                a tuple (Table, join_condition). Is None when no join is needed and is False
                if the len(path) > 1 (as in address__city__country__in=...)
      
    return: joins, op, op_str, value, col, join_args
    Es.::

     >>>> djs.django2components(Address.__mapper__, {'date_created__gte' : 'm'})
     ([], '>=', 'gte', 'm', Column('date_created', Date(), table=<address>), None)
     >>>> djs.django2components(Address.__mapper__, {'user_id__first_name' : 'ed'})[:-1]
     (['user_id'], '=', 'eq', 'ed', Column('first_name', String(length=50, convert_unicode=False, assert_unicode=None), table=<user>),
           (Table('user', MetaData(Engine(sqlite://)), ...),
            ,<sqlalchemy.sql.expression._BinaryExpression object at 0x8859cec>)))
    

    """
    if isinstance(mapper_or_table, Table):
        mapper = None
        
        table = mapper_or_table
    else:
        mapper = mapper_or_table
        table = mapper.local_table
        
    name = kw.keys()[0]
    value = kw[name]
    tokens = name.split('__')
    joins = []
    join_args = None
    
    if len(tokens) == 1:  # field_name='abc'
        op_str = 'eq'
        attr = tokens[0]
        try:
            col = getattr(table.columns, attr)
        except AttributeError, e:
            col = getattr(mapper.c, attr)
        value = kw[attr]

    else:  # data_gte=today() -- address__city__country__in=['Italy','France']
        if tokens[-1] in OPERATORS:
            op_str = tokens.pop()
        else:
            op_str = 'eq'
        attr = tokens.pop()
        if tokens: # may be consumed by now...
            joins = deepcopy(tokens)
            col = get_foreign_column(mapper, path=tokens, attr=attr)

            if len(joins) > 1:
            ## I'm not going to calculate join conditions for longer path... too complex now
                join_args = False
            else:
                ## this is used in 2 cases: the join on a foreign key, so that order_by can work
                ## correctly, and possibly filter can avoid a subselect
                try:
                    col0 = getattr(mapper.columns, joins[0], None)
                except AttributeError, e:
                    # i think this is never really tested. It was here when I used to pick the
                    # element from the table but when using mapper/table expressing joins
                    # the name of the column changes while  mappers have the name we expect
                    col0 = getattr(table.columns, joins[0], None)
                if col0 is not None:
                    join_args = (col.table, col0 == col0.foreign_keys.copy().pop().column)
                else:
                    join_args = False
        else:
            join_args = None
            try:
                col = getattr(table.columns, attr)
            except AttributeError, e:
                col = getattr(mapper.c, attr)
            #col = table.columns[attr]

    op = OPERATORS[op_str]
    if op_str in ('regexp', 'iregexp'):
        op, value = get_regexp_op(table.metadata.bind.name, op_str, value)

    return joins, op, op_str, value, col, join_args

def get_foreign_column(mapper, path=None, attr=None):
    """
    follow PropertyLoaders chain to get the last referenced column
    """
    path = deepcopy(path)
    if not mapper:
        raise NotImplementedError("Can't cross relationship if you don't provide a mapper")

    prop = mapper.get_property(path.pop(0))
    for elem in path:
        prop = prop.mapper.get_property(elem)
    return get_column(prop, attr)


def django2query(query, mapper_or_class, OR=False, aliased=False, OUTER=False, **kw):
    """
    return a new query with new constraints expressed in  'django-style'

    :param query:     the query to which filters will be applied
    :param mapper_or_class: a mapper or a class from which the class will be devised
    :param aliased: passed to :class:`DjangoParser`
    :param OUTER: :class:`DjangoParser` will be instantiated as an OUTER join
    """

    from sqlalchemy.orm import class_mapper, Mapper

    mapper = mapper_or_class
    if isinstance(mapper_or_class, Mapper):
        mapper = mapper_or_class
    else:
        mapper = class_mapper(mapper_or_class)
        
    parser = DjangoParser(mapper, query, OR=OR, aliased=aliased, outer=OUTER)

    for key,val in kw.iteritems():
        parser.parse( {key:val})

    return parser.compose()


def django2sqlalchemy(mapper=None, table=None, OR=False, **kw):
    """
    Return a tuple (ClauseList, join path).

    :param mapper: the mapper that will be used in the query
    :param table: the mapper that will be used in the query
    :param OR: if True the conditions will be ORed
    :param kw: the conditions as per django-like syntax
    """
    if table:
        parser = DjangoParser(table, query=None, OR=OR)
    else:
        parser = DjangoParser(mapper, query=None, OR=OR)

    for key,val in kw.iteritems():
        parser.parse( {key:val})
    return parser.sql(), parser.joins

def get_column(prop, attr):
    """
    return the column(s?) referenced from a property
    """
    if isinstance(prop, ColumnProperty):
        col = prop.columns[0]
        if col.foreign_keys:  ## FIXME: Should I consider multiple fkey?
            return getattr(col.foreign_keys.copy().pop().column.table.c, attr)
        else:
            return prop.columns[0]  ### FIXME: why colums is a list?
    elif isinstance(prop, PropertyLoader):
        return getattr(prop.mapper.local_table.c, attr)  
    
def path2join(path, mapper):
    table = mapper.local_table
    join = table
    for elem in path:
        for token in elem:
            prop = mapper.get_property(token)
            if isinstance(prop, ColumnProperty):
                col = prop.columns[0]
                if col.foreign_keys:  ## FIXME: Should I consider multiple fkey?
                    table = col.foreign_keys.copy().pop().column.table
            elif isinstance(prop, PropertyLoader):
                table = prop.remote_side[0].table

            join = join.join(table)

    return join

def get_regexp_op(bind_name, op_str, value):
    """
    return the best approximation to regexp operator
    in sqlite fall back to (I)LIKE
    """
    if bind_name.startswith('postgres'):
        if op_str == 'regexp':
            return '~', value
        else:
            return '~*', value
    elif bind_name.startswith('mysql'):
        return 'REGEXP', value
    else:
        return 'like', '%' + value + '%'
    





