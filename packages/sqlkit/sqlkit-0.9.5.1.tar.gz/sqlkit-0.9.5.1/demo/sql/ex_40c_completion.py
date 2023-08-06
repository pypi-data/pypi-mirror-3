"""completion/filter on fkey

filters on foreign key start (and are constraint) in the referenced table

"""

lay = """
   title
   year
   director_id
   date_release
"""

t = SqlMask(model.Movie, dbproxy=db, layout=lay)
t.completions.director_id.filter(nation='IT')




