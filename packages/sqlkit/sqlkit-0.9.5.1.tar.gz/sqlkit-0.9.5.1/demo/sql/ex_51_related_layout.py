"""layout/layout of a related treeview

Layout can be also set for related table

Try right-clicking on a film and open the movie with layout set by layout_movie

"""


lay_director = """
     last_name
     m2o=movies -
"""

lay_movie = """
    title
    year
    m2m=actors -
"""

t = SqlMask(model.Director, dbproxy=db, layout=lay_director,
            order_by='last_name')
t.related.movies.layout = lay_movie

t.reload()

