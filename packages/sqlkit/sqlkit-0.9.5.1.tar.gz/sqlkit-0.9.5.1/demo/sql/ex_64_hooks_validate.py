"""hooks/on_validation - related

you can also change a related validation be sure you understand when you
have to check a sqlkit or a related one.  If you want to prevent a change
in a related table where you cannot edit (as is the genres table), you must
set the check on the validation of attribute 'genres' of the main Mask.

On the contrary the completion on genres takes place in the related table,
so that you need to add __genres__ to the name of the method

"""
from sqlkit.exc import ValidationError
from sqlkit.db.utils import get_differences

class Hooks(object):
    def on_field_validation__genres(self, mask, field_name, field_value, field):
        for field_name, old, new in get_differences(mask.current):
            if field_name == 'genres':
                raise ValidationError("I don't want you to change the genre!!!")
        
    def on_completion__genres__name(self, mask, field_name, obj):
        print "No, please, don't change the genres..."


lay = """
   title
   year
   director_id
   m2m=genres -
   """

t = SqlMask(model.Movie, layout=lay, label_map={'genres.name':'genres'},
         dbproxy=db, hooks=Hooks())

t.reload()

