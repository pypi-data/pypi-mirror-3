"""mapper & fields/filter: adding column

The output is represented ina tab of the Filter Panel and
can be customized

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

count_movies = CountMovies('n_movies', {'length' : 4})


t = SqlMask(model.Director, dbproxy=db)
col = columns.VarcharColumn(t, 'n_movies', 'Movie Count', field=count_movies)
t.gui_fields['n_movies'] = count_movies
t.filter_panel.view.add_column(col)
t.filter_panel.show()
t.filter_panel.reload()

