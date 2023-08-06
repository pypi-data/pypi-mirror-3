"""completion/autostart

Completion may start automaticaly after n digits entered
Try writing 2 letter (eg.: 'fa')

"""

lay = """
   title
   year
   director_id
   date_release
"""

t = SqlMask(model.Movie, dbproxy=db, layout=lay)
t.completions.director_id.autostart = 2



