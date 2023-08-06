"""completion/group by

the values shown in a completion may be grouped 
try completion on 
"""

lay = """
    title
    year
    director_id
"""

import gobject

t = SqlMask(model.Movie, dbproxy=db, layout=lay)
t.completions.director_id.group_by = 'nation'
gobject.idle_add(t.completions.director_id.show_possible_completion, None, 'start')



