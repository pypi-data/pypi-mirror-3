"""base/filters vs. constraints

a filter can be added with django_like syntax
"""

t = SqlTable('director', dbproxy=db,  order_by='last_name',  )
t.add_filter(last_name__icontains='a')
t.reload()

t2 = SqlTable('director', dbproxy=db,  order_by='last_name',  )
t2.add_constraint(last_name__icontains='a')
t2.reload()

t = t2
