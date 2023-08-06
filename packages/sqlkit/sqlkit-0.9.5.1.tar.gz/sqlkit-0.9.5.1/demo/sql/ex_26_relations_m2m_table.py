"""relation/m2m - different packing

Now the SqlTable for genres and actors are placed in a Table
that needs to be made to expand. You may notice that the separator
between genres and actor is no longer aligned with the end of the
title antry.
"""

lay = """
         title       year
         director_id - - -
         {T.a m2m=genres:5   m2m=actors } - - -
         """
t = SqlMask(model.Movie, dbproxy=db , layout=lay)

Tbl = t.widgets['T.a']
Tbl.get_parent().child_set_property(Tbl, 'y-options', gtk.EXPAND|gtk.FILL)

