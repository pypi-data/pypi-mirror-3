"""base/totals

A silly example to show the total on an integer.

Here images are rendered as icons as the argument to SqlTable is a model
class rather that a simple string. No reflection is done, the model is read
from file and the model has more info to explain how to display it as well.

"""

t = SqlTable(model.Movie,
             dbproxy=db,
             order_by='director_id',
             rows=30,
             geom=(800,600)
         )

t.totals.add_total('year')
t.totals.add_break('director_id')

t.reload()

