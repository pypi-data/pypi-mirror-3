"""printing/foreign key

How to cope with foreign keys. The template has '$director_id', that will be
rendered as the last_name of the Director instead of the id that is the
value of the foreign key attribute.

This happens becouse the main object and the objects in 'Table1' are wrapped into ObjProxy, a
proxy that follows the foreign key and retrieves the "correct" (well, best match) value.

"""

lay = """
  title
  year
  date_release
  director_id
"""

t = SqlMask(model.Movie, layout=lay, dbproxy=db)
t.printing.add_menu_entry('Print to pdf', 'movie-fk.odt', mode='pdf', accel='<Alt>p')
t.reload()


