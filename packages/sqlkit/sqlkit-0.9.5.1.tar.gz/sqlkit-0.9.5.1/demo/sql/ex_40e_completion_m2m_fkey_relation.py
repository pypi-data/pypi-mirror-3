"""completion/m2m fkey - relation

In this case we added  filter on a relation of the base record that is actor
"""

lay = """
     title       year
     director_id - - -
     m2m=actors:nation_cod,last_name,first_name - - -
"""

t = SqlMask(model.Movie, dbproxy=db , layout=lay)
t.related.actors.completions.nation_cod.filter(nation__nation='France')
