"""base/filters: relative dates

A filter may be expressed as a relative interval from now.
read complete documentation on here:
  http://docs.argolinux.org/sqlkit/sqlkit/filters.html

But for now you can play with symbolic math: y for year, m for month,
d for day, w for week.

the '>' sign sets a period.

This allows to express dates in a very natural way. particularly when you need
to save queries

"""

t = SqlTable('movie', dbproxy=db, geom=(600, 400))
t.add_filter(date_release__gte='y-1 +2m')
t.reload()

t2 = SqlTable('movie', dbproxy=db,  geom=(600,400))
t2.add_filter(date_release__gte='y-5 > y-2')
t2.reload()

t = t2
