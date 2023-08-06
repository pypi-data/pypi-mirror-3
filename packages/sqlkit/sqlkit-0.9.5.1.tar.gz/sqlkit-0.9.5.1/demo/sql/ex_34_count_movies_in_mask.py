"""mapper & fields/adding field in mask

A field can be added to a mask as well


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


LAYOUT = """
  last_name
  n_movies
"""

t = SqlMask(model.Director, dbproxy=db, layout=LAYOUT,
                 gui_field_mapping = {'n_movies' : CountMovies}
                 )
t.reload()
