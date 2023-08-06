"""hooks/warning - related

Very similar to the precedent but with warning on a related table

"""
from sqlkit.exc import ValidationError, ValidationWarning
from sqlkit.db.utils import get_differences

class Hooks(object):
    def on_field_validation__genres(self, mask, field_name, field_value, field):
        for field_name, old, new in get_differences(mask.current):
            if field_name == 'genres':
                msg = "I'd really prefer you don't change genre!!!"
                raise ValidationWarning(msg)
        
lay = """
   title
   year
   director_id
   m2m=genres -
   """

t = SqlMask(model.Movie, layout=lay, label_map={'genres.name':'genres'},
         dbproxy=db, hooks=Hooks())

t.reload()

