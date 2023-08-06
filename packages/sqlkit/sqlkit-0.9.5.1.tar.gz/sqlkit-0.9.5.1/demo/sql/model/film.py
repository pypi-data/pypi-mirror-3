#!/usr/bin/python

from  sqlkit.widgets import *
import gtk
import movies


lay = """

  { first_name last_name}
  o2m=movies:title,date_release,description,year

"""

t = SqlMask(Class=movies.Director, dbproxy=movies.db,
             single=True, layout=lay)
t.reload()


gtk.main()


