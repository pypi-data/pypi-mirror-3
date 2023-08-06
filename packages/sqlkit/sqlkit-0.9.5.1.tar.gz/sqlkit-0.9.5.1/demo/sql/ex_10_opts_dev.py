"""base/options: dev

developer mode show id as well. hide/field_list prevail on this mode.
default is False.
"""

t = SqlTable('movie',
             dbproxy=db,
             order_by='director_id',
             dev = True,
         )


t.reload()

