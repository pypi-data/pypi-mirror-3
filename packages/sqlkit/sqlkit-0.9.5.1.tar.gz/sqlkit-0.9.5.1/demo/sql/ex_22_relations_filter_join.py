"""relation/o2m: filtering

Adding filters again: now filters span relationships. A '__'  underscore
separates the property from the operator and the property of one table
to a related table one's.

Iregexp is rendered with like in sqlite, with ~* in postgres

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

