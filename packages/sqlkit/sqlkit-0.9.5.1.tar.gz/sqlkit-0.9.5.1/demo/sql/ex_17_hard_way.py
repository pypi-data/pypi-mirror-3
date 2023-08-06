"""base/join - explicit

you can pass a mapper that already has the join as you prefere

It you explicitely define mapping for attribute 'id', it
will prevent SA from complaining about 2 columns with same name

"""

from sqlalchemy.orm import join, mapper

class Join(object): pass
        
m = mapper(Join, model.Movie.__table__.join(model.Director.__table__),
           properties={
                 'movie_id' : model.Movie.__table__.c.id
            })



t = SqlTable(m, dbproxy=db )
t.add_filter(director_nation='IT')
t.reload()

