"""completion/m2m fkey

Let's see an m2m relation with one field that is a ForeignKey (nation_cod),
and a filter added to completion for 'nation_cod'.

The filter acts on the select of the m2m record, so that 'nation_cod'=IT
becomes a filter for the whole record selected.

A .filter() on an m2m completion, acts on *all* completions as it just
determines the constraints on the whole record.

"""

lay = """
     title       year
     director_id - - -
     m2m=actors:nation_cod,last_name,first_name - - -
"""

t = SqlMask(model.Movie, dbproxy=db , layout=lay)
t.related.actors.completions.nation_cod.filter(nation_cod='IT')
