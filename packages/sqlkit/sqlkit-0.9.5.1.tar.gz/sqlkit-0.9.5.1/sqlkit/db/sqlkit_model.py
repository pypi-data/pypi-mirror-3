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
.. _sqlkit_model:

SQLkit models
==============

Sqlkit does not need any private table, but can take advantage from the
presence of a couple of them to handle via database some trivial jobs.

tables
-------

The jobs that can be esied by the presence ot these tables
are:


  1. definition of format string to be used when showing a completion on
     foreign key fields:
     this can be eg: ``%(first_name)s %(last_name)s`` to use composition
     of first and last name to represent a person. If this is not set,
     the description field of the foreign table is used (see below)

  2. search_format: field_name that should be searched for in completion.
     This must be a single field. In case this is not set the first chhar
     field is taken.
     
fields
-------

  1. name that should appear in the layout for each field
  
  2. autostart completion (not yet)
  
  3. help_text: text to be represented in a tooltip

sqledit hook
------------

you can edit these tables directly from sqledit with the option --configure::

  sqledit --configure sqlite://
  

"""
import re

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, String, Integer, ForeignKey
from sqlalchemy.orm import relation

import utils

Base = declarative_base()

def get_classes(bind):

    global SqlkitTable, SqlkitFields
    try:
        return SqlkitTable, SqlkitFields
    except:
        if re.match('firebird', bind.name):
            SQLKIT_TABLE = 'sqlkit_table'
            SQLKIT_FIELD = 'sqlkit_field'
        else:
            SQLKIT_TABLE = '_sqlkit_table'
            SQLKIT_FIELD = '_sqlkit_field'

        class SqlkitTable(Base, utils.Descr):
            __tablename__  = SQLKIT_TABLE
            name           = Column(String(100), primary_key=True)
            search_field   = Column(String(50))
            format         = Column(String(150))

        class SqlkitFields(Base, utils.Descr):
            __tablename__ = SQLKIT_FIELD
            table_name    = Column(String(100), ForeignKey('%s.name' % SQLKIT_TABLE),
                                   primary_key=True)
            name          = Column(String(100), primary_key=True)
            description   = Column(String(100))
            help_text     = Column(String(300))
            regexp        = Column(String(100))
            autostart     = Column(Integer)
            default       = Column(String(200))
            table         = relation('SqlkitTable', backref='attributes',
                                     primaryjoin = table_name == SqlkitTable.name)

        return SqlkitTable, SqlkitFields
