#!/usr/bin/python

import sys

from sqlkit import debug as  dbg
#dbg.debug(True)
dbg.debug(True, gtk=True)
dbg.trace_class(ok='SqlTable|SqlWidget|SqlMask|Completion')
but = 'set_fkey_descr|(lookup|set|get)_value|[el]ne_cb|match_func' + \
       '|cell_default_cb|cell_bool_cb'
dbg.trace_function(exclude=but)

import sqlkit
from sqlkit.widgets import SqlTable, SqlMask
from sqlkit.db import proxy, defaults, utils
import gtk


db = proxy.DbProxy(engine="sqlite:///../../demo/sql/model/movies.sqlite")
session = db.get_session()
utils.TableDescr('director', format='%(first_name).1s. %(last_name)s',
                 metadata=db.metadata)
utils.TableDescr('movie', format='%(title)s. %(year)s',
                 metadata=db.metadata)
def_director = defaults.Defaults('director', metadata=db.metadata)
def_director.set_defaults( {'first_name':'nome...',})


def_movie = defaults.Defaults('movie', metadata=db.metadata)
#def_movie.fk( 'director_id', 'last_name', 'Olmi')

lay = """
   first_name
   last_name
   nation
   o2m=films -
"""


if 'm' in sys.argv:
    t = SqlMask('director', dbproxy=db, single=True, layout=lay)
    
else:
    t = SqlTable('director', dbproxy=db, single=True, dev=False,
                  order_by='last_name',
                  rows=6,
                  #field_list='director_id,title'
                  )
#    t.reload()

t.completions.last_name.filter(nation='$nation')
    
#    t.totals.add_total('year')
#t.mapper.local_table.metadata.bind.echo = True

#t.completions.director_id.autostart=1
try:
    gtk.main()
except KeyboardInterrupt:
    pass



