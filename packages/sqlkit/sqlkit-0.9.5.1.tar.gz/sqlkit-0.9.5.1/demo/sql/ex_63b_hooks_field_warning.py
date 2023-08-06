"""hooks/warning - on_field_validation

A warning will not make validation to abort, but will just warn the user
and give an opportunity to proceed or go back editing.

In this case you may want to implement firther actions in after_flush
"""
from sqlkit.exc import ValidationWarning

class Hooks(object):

    def on_field_validation__year(self, mask, field_name, field_value, field):
        if field_value > 2020:
            raise ValidationWarning("You can go on, but it's strange!...")

    def on_after_flush(self, mask, obj, session):
        if mask.current.year > 2020:
            print "Funny guy who know the future (%s)!" % mask.current.year

lay = """
   title
   year
   director_id
   m2m=genres -
   """

t = SqlMask(model.Movie, layout=lay, label_map={'genres.name':'genres'},
         dbproxy=db, hooks=Hooks())

t.reload()

