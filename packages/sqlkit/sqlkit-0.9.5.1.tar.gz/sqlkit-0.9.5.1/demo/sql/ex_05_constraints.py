"""base/constraints

A table/mask can be constrained to only browse a subset of the real data.
This means that additional filters (possibly spanning joined relations) are
applied to the query when issuing.


Commented out is the SQLAlchemy syntax for the same filter
"""


## Example 1: movies older tha 2000
t = SqlTable(model.Movie, dbproxy=db)
t.add_constraint(year__lt=1996)
#t.query = t.query.filter(t.mapper.c['year'].op('<')(1996))

t.reload()

## Example 2: constraints on related director as well
t1 = SqlTable(model.Movie, dbproxy=db)
t1.add_constraint(director__nation='IT', year__lte=2000, OR=True)

# from sqlalchemy.sql import and_, or_
# nation = model.Director.__mapper__.c['nation']
# filter_condition = or_(nation.op('=')('IT'), t1.mapper.c['year'].op('<=')(2000))
# t1.query = t1.query.join('director').reset_joinpoint().filter(filter_condition)
t1.reload()


