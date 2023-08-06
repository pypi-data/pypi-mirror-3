"""base/tree table

Tree Table
----------

In this example a table is displayed with gerarchical grouping

"""

from sqlkit.widgets.table.modelproxy import Header, ModelProxy

class MyModel(ModelProxy):

    def make_header_obj(self, field_value):

        return Header(self.master, 'title', self.master.gui_fields.director_id.get_human_value(field_value))


t = SqlTable('movie', dbproxy=db, order_by='title', )
t.modelproxy = t.modelproxy.copy(MyModel)
t.modelproxy.tree_field_name = 'director_id'
t.hide_fields('director_id')
t.reload()

