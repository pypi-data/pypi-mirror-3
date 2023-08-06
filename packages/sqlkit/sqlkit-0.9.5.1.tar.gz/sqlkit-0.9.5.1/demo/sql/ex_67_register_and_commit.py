"""hooks/on_init

in this example, a hook is registered that has hooks on commit and the
table is used as an m2m. 

At this point you see that the hook is called 2 times. That's becouse the
session extension is called 2 times inside t.commit(), since default sesion for
sqlkit is autocommit=True and in t.commit() a t.session.begin() triggers
the first commit, followed by a second one explicitely requited.

"""
from sqlkit.db.utils import get_differences
from sqlkit.db import register_hook

class MovieHooks(object):

    def on_after_commit(self, widget, obj, session):
        print "on_after_commit hook from %s" % widget, obj


register_hook('movie', MovieHooks)

lay = """
    last_name
    o2m=movies -
"""

t = SqlMask(model.Director, dbproxy=db, layout=lay,)
t.reload()

