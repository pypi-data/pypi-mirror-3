"""hooks/on_validation - related

Hore we change the related hook just to see that both hooks get called.

"""
from sqlkit.exc import ValidationError
from sqlkit.db.utils import get_differences

class HooksDirector(object):
    def on_validation__movies(self, table):
        print "called validation on *MAIN* (relationship_leader) table movies", table
        
    def on_change_value__movies__title(self, table, field_name, field_value, field):
        print "called on_change_value__movies__title on *MAIN* (relationship_leader) table movies", table

class HooksMovies(object):
    def on_validation(self, table):
        print "called validation on movies DIRECTLY", table

    def on_change_value__title(self, table, field_name, field_value, field):        
        print "called on_change_value__title on movies *DIRECTLY*  table movies", table
        

lay = """
   first_name last_name
   o2m=movies - - -
   """

t = SqlMask(model.Director, layout=lay,
         dbproxy=db, hooks=HooksDirector())

## you can change hooks any time just assigning it
t.related.movies.hooks = HooksMovies()

t.reload()

