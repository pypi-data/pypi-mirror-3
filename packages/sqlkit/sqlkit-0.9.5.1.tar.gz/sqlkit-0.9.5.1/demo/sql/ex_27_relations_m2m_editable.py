"""relation/m2m - editable

Actors can now be added from here.

"""

lay = """
         title       year
         director_id - - -
         m2m=actors  - - -
         """
t = SqlMask(model.Movie, dbproxy=db , layout=lay)
t.related.actors.set_editable(True)



