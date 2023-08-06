"""completion/filter

you can enforce a constraint on the values returned by completion

"""

lay = """
   title
   year
   director_id
   date_release
"""

t = SqlMask(model.Movie, dbproxy=db, layout=lay)
t.completions.title.filter(title__icontains='a')


