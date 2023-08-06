"""mapper & fields/adding count 

This is an alternative way to add a movie count field that adds a column
When going this way you cannot filter on the "Movie Count" column
"""

from sqlkit import fields
from sqlkit.widgets.table import columns
from sqlkit.db.utils import DictLike

class CountMovies(fields.IntegerField):
    """
    A field that counts the movies
    """
    @fields.std_cleanup
    def clean_value(self, value):
        ## missing a field_name attribute on obj the objct itselt is passed
        return len(value.movies)

count_movies = CountMovies('n_movies')



t = SqlTable(model.Director,    dbproxy=db)

## add the fields to gui_fields
t.gui_fields['n_movies'] = count_movies
## create a column
col = columns.VarcharColumn(t, 'n_movies', 'Movie Count', field=count_movies)
## add it to the view
t.views['main'].add_column(col, position=2)
#t.field_list += ['n_movies']

t.totals.add_total('n_movies')

t.reload()

