"""hooks/on_after_flush

This hook is completely similar to 'after-flush' signal, but is meant to be
defined in a separate class so that it's easier to propagate validation hooks
to a spawned child (RecordInMask) 

Open a mask right clicking on a record, change something and save. You'll see
that on_after_flush is called eather.

"""
from sqlkit.db.utils import get_differences

class Validation(object):

    def on_after_flush(self, table, obj, session):

        for o in session.new:
            print "New object: %s" % o
        for o in session.dirty:
            print "Updated objects: %s" % o
            for field_name, old, new in get_differences(o):
                print "%s: %s ==> %s" % (field_name, old, new)

        for o in session.deleted:
            print "Deleted objects: %s" % o


t = SqlTable(model.Director, dbproxy=db,
             order_by='first_name', hooks=Validation(),)
t.reload()

