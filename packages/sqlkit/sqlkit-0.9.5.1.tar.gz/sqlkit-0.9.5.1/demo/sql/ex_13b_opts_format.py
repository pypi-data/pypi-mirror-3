"""base/options: format (numbers)

Numbers will be represented according to active locale (according to
environment variables LC_NUMERIC, LC_ALL, LANG).

It's possible to force a different representation setting 'format' and possibly
'locale' on the vfields. That can be done with set_format method or via
'format' argument.
"""

t = SqlTable('movie',
             dbproxy=db,
             order_by='director_id',
             rows = 15,
             format = {'year': '#'}, # don't use group separator
         )


t.reload()

