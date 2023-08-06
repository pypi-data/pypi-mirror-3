#!/usr/bin/python 

import sys
import gtk

sys.path.insert(0, '../..')
import dbg
# dbg.debug(True, gtk=True)  # uncommenti this to get gtk debug treeview

dbg.trace_class(ok='SqlTable|SqlWidget|SqlMask')
but = 'set_fkey_descr|(lookup|get)_value|[el]ne_cb|match_func' + \
       '|cell_default_cb|cell_bool_cb|lookup_value|is_fkey|instance2'
dbg.trace_function(exclude=but)

import elixir
from datetime import datetime, timedelta

import time
import sqlkit 
from sqlkit.db import proxy
from sqlkit import completion

elixir.metadata.bind = "sqlite:///movies.sqlite"
db = proxy.DbProxy(engine="sqlite:///movies.sqlite")
__metadata__ = db.metadata

class Director(elixir.Entity):
    last_name = elixir.Field(elixir.String(60))
    first_name = elixir.Field(elixir.String(60))
    movies = elixir.OneToMany('Movie', inverse='director', lazy="False")
#    movies = elixir.OneToMany('Movie', inverse='director', lazy="False", cascade="all, delete-orphan" )
    elixir.using_options(tablename='director')

    def __repr__(self):
        return u'<Director: %s>' %self.last_name

class Movie(elixir.Entity):
    title = elixir.Field(elixir.String(60))
    description = elixir.Field(elixir.String(512))
    year = elixir.Field(elixir.Integer())
    director = elixir.ManyToOne('Director', inverse='movies' , lazy="False")
    elixir.using_options(tablename='movie')

    def __repr__(self):
        return u'<Movie: %s>' % self.title


elixir.setup_all()

lay = """first_name last_name
         o2m=movies      - - -
         """
tm = sqlkit.SqlMask(Director.mapper, metadata=__metadata__, session=elixir.session,layout=lay)
t = tm.vfields['movies'].widget.table


gtk.main()
