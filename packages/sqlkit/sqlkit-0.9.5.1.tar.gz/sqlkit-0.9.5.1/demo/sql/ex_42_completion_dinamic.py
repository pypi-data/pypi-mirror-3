"""completion/dinamic filter 

A filter on completions may also be based on value of onother field in the
moment the competion is invoked.

Here the contrainst is on nation. The completion of director is constrained by a possible value entered in nation.
"""

lay = """
   last_name
   nation
"""

import gobject
t = SqlMask(model.Director, dbproxy=db, layout=lay)

t.completions.last_name.filter(nation='$nation')

gobject.idle_add(t.set_value,'nation', 'IT')

t2 = SqlMask(model.Director, dbproxy=db, layout=lay)

