"""base/options: rows

rows sets the number of rows it should display. Almost working...
Depending on style.
"""

t = SqlTable('movie',
             dbproxy=db,
             order_by='director_id',
             rows = 15,
         )


t.reload()

