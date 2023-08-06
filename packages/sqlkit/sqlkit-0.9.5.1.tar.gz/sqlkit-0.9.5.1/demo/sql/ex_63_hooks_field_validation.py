"""hooks/on_field_validation on_save_as

you can set hooks on single field validation. It will be called from within
the field. The hook 'on_save_as' is called when a record is duplicated.


"""
from sqlkit.exc import ValidationError

class Hooks(object):

    def on_field_validation__year(self, mask, field_name, field_value, field):
        if field_value > 2020:
            raise ValidationError("Hei: how can you know the future!")

    def on_save_as(self, mask, old, new):
        print "Old title: %s, \nnew title: %s" % (old.title, new.title)


lay = """
   title
   year
   director_id
   m2m=genres -
   """

t = SqlMask(model.Movie, layout=lay, label_map={'genres.name':'genres'},
         dbproxy=db, hooks=Hooks())

t.reload()

