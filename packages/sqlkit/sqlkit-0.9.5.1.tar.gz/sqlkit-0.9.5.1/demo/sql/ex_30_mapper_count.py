"""mapper & fields/nested select

this is an example of a mapper with a nested select.

You can still use filters and constraints
"""

from sqlalchemy.orm import mapper, column_property
from sqlalchemy.sql import select, func

class Director2(object): pass

m = mapper(Director2, model.Director.__table__,
   properties={
    'film_number': column_property(
            select(
                [func.count(model.Movie.__table__.c.id)],
                model.Director.__table__.c.id == model.Movie.__table__.c.director_id
            ).label('film_number')
        )
  }
)

field_list = "last_name, first_name, nation, film_number"
t = SqlTable(m, field_list=field_list, dbproxy=db)
t.add_filter(film_number=3)
t.add_constraint(film_number__lt = 5)
t.reload()



