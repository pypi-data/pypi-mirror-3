"""completion/autostart m2m

Completion may start automaticaly after n digits entered
Try writing 2 letter (eg.: 'fa')

"""

lay = """
   title
   year
   director_id
   m2m=genres -
"""

t = SqlMask(model.Movie, dbproxy=db, layout=lay)
t.related.genres.completions.name.autostart = 2

