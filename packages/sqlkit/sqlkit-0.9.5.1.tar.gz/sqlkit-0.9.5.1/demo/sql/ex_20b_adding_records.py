"""relation/adding records

Adding a relation is as easy as adding the relation name to the layout.
Note that in this case the table name is not sufficient, we need to know
the mapping so we pass a class_ attribute that is really a mapped class
(in this example built with declarative layer)

"""

lay = """
   first_name
   last_name
   nation
   m2m=movies -
"""

t = SqlMask(model.Director, dbproxy=db, layout=lay)
t.add_filter(last_name='Faenza')
t.filter_panel.reload()


r = t.related.movies
r.totals.add_total('year')
f = r.mapper.class_()
f.title = 'Alla luce del sole'
r.add_record(f)





