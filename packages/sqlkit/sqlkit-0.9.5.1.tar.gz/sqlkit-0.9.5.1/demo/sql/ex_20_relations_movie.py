"""relation/o2m

Adding a relation is as easy as adding the relation name to the layout.
Note that in this case the table name is not sufficient, we need to know
the mapping so we pass a class_ attribute that is really a mapped class
(in this example built with declarative layer)

"""

lay = """
   first_name
   last_name   nation
   m2m=movies - - -
"""

t = SqlMask(model.Director, dbproxy=db, layout=lay)

t.reload()

