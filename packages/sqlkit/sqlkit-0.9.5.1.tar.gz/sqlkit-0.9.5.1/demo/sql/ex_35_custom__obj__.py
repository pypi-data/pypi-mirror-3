"""mapper & fields/filter: customize default 

A field can be added to a mask as well


"""

from sqlkit import fields
from sqlkit.widgets.table import columns
from sqlkit.db.utils import DictLike

class Director(fields.VarcharField):
    """
    A field that counts the movies
    """
    length = 30

    @fields.std_cleanup
    def clean_value(self, value):
        ## missing a field_name attribute on obj the objct itselt is passed
        return "Customized: %s" % value.last_name 


LAYOUT = """
  first_name
  last_name
"""

t = SqlMask(model.Director, dbproxy=db, layout=LAYOUT,   )
t.filter_panel.replace_column(Director)
t.filter_panel.show()
t.filter_panel.reload()
