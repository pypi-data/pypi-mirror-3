"""base/opts: order_by - foreign_key

Order by can use django_syntax too

"""

t = SqlTable('movie',
             dbproxy=db,
             order_by='director_id__last_name',
             geom=(800,300),
             )

# the following is ok too:
# t.order_by = 'director_id__last_name'

t.reload()

