"""mapper & fields/adding fields

You can add fields to the table by:

  * creating a fields (sqlkit.widgets.common.Fields)
  * adding it to gui_fields dict
  * adding a column that uses that field

It won't be editable as it does not have a correspondence with
any database field and you wont be able to filter by that field,
but you can sort on that field and it will be exported reglarly
when the table is exported.

"""

from sqlkit import fields
from sqlkit.widgets.table import columns
from sqlkit.db.utils import DictLike

class ObjField(fields.VarcharField):
    """
    A field that presents the obj 
    """
    @fields.std_cleanup
    def clean_value(self, value):
        return "%(year)s %(title)s" % DictLike(value)
    



t = SqlTable('movie',    dbproxy=db, order_by='title', )
t.views['main'].add_column(field=ObjField('new_column', {'length' : 30}), position=0)

# in sqlkit < 0.9.2 you would have splitted the operations as follows:
# my_field = ObjField('new_column', {'type' : str, 'length' : 30})
# ## add the fields to gui_fields
# t.gui_fields['new_column'] = my_field
# ## create a column
# col = columns.VarcharColumn(t, 'new_column', 'My New Column', field=my_field)
# ## add it to the view
# t.views['main'].add_column(col, 0)

t.reload()

