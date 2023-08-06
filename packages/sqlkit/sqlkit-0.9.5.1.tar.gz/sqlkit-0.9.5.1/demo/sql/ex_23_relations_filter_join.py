"""relation/o2m: reload filter panel

Reloading from the filter panel is slightly different: it shows the result
in a page of the filter panel.

str(obj) is used to represent the records.
"""

lay = """
   first_name
   last_name
   nation
   m2m=movies::title,year -
"""

t = SqlMask(model.Director, dbproxy=db, layout=lay)
t.add_filter(movies__title__icontains='il')
t.add_filter(first_name__icontains='a')
t.reload()

