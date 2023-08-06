#!/usr/bin/python

from sqlkit import debug as dbg

dbg.debug(True)
dbg.debug(True, gtk=True)
dbg.trace_class(ok='SqlTable|SqlWidget|SqlMask|Completion')
but = 'set_fkey_descr|(lookup|get)_value|[el]ne_cb|match_func' + \
       '|cell_.*_cb|lookup_value|is_fkey|instance2|markup_clean|get_iter'
dbg.trace_function(exclude=but)

from  sqlkit.widgets import *
import gtk
import movies


field_list="integer, float numeric"
field_list=None

table = movies.AllTypes.__table__
table = movies.Movie.__table__

# t = SqlMask(table=table, dbproxy=movies.db,
#              field_list=field_list, single=True)

t = SqlTable(table=table, dbproxy=movies.db,
             field_list=field_list, single=True)
#t.reload()


gtk.main()


