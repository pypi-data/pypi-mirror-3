"""hooks/on_activate

on_activate if run when you press Return in the field.

"""

class Validation(object):
    def on_activate__first_name(self, mask, field_name, field):
        print "he's name is %s and comes from %s" % (
            field.get_value(), mask.get_value('nation'))

    on_activate__last_name = on_activate__first_name

t = SqlMask(model.Director, dbproxy=db,
            order_by='last_name', hooks=Validation() )

t.reload()

