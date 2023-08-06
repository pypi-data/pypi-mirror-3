"""hooks/on_validation

on_validation is triggered any time you save. Here you can implement a read
only table...

try changing something and then saving.

"""
from sqlkit.exc import ValidationError
from sqlkit.db.utils import get_differences

class Validation(object):
    def on_validation(self, mask):

        changed = False
        for field_name, old, new in get_differences(mask.current):
            print field_name, old, new
            changed = True

        if changed:
            raise ValidationError("I don't want you to change anything!!!")

t = SqlMask(model.Movie, dbproxy=db, hooks=Validation())
t.gui_fields.description.blank = True  #don't try to change '' in None

t.reload()

