"""base/options: hide

year and description will not be visible

"""

t = SqlTable('movie',
             dbproxy=db,
             order_by='director_id',
             hide_fields='year, description',
         )


t.reload()

