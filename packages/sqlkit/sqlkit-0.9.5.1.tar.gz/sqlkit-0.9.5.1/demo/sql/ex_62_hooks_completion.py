"""hooks/on_completion

on_completion is triggered any time you choose from a completion.
Argument obj can be accessed both as dict or as obj.
"""

class Hook(object):
    def on_completion__director_id(self, mask, field_name, obj):
        print vars(obj)
        print "Was this film directed by %s %s?" % (obj.last_name)


t = SqlMask(model.Movie, dbproxy=db, hooks=Hook())

t.reload()

