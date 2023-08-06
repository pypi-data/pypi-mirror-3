#!/usr/bin/python 

import sys
import gtk
from sqlkit import debug as  dbg
dbg.debug(True, gtk=True)
dbg.trace_class(ok='SqlTable|SqlWidget|SqlMask|Completion')
but = 'set_fkey_descr|(lookup|get)_value|[el]ne_cb|match_func' + \
       '|cell_default_cb|cell_bool_cb|lookup_value|is_fkey|instance2'
dbg.trace_function(exclude=but)

#from elixir_model import Director, Movie, Actor, Genre
#from db_model import Director, Movie, Actor, Genre
from db_model_autoload import Director, Movie, Actor, Genre

import sqlkit
from sqlkit.db import proxy
from sqlkit import completion
from sqlkit.db.utils import TableDescr

db = proxy.DbProxy(engine="sqlite:///movies.sqlite")
TableDescr('director', format="%(first_name)s %(last_name)s",
           metadata=db.metadata)

TableDescr('movie', format="%(title)s (%(year)s)",
           metadata=db.metadata)


lay = """
         title       year:5< 
         director_id - - -
         {T.a m2m=genres:5   m2m=actors:5:first_name,last_name } - - -
         """
t = sqlkit.SqlMask(Movie, dbproxy=db , layout=lay)
#t.add_constraint(genres__name__like='sto%')
Tbl = t.widgets['T.a']
Tbl.get_parent().child_set_property(Tbl, 'y-options', gtk.EXPAND|gtk.FILL)
                 
t.reload()
t.mapper.local_table.metadata.bind.echo = True

gtk.main()
