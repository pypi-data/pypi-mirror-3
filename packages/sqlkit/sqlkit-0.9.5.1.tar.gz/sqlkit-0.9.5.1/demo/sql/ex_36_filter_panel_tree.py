"""mapper & fields/filter: grouping

The output view of a filter panel can be grouped 


"""

from sqlkit.widgets.table import Header, ModelProxy

class MyModel(ModelProxy):

    def make_header_obj(self, field_value):

        return Header(self.master, 'director_id', field_value)

t = SqlMask(model.Movie, dbproxy=model.db, )
t.modelproxy = t.modelproxy.copy(MyModel)
t.modelproxy.tree_field_name = 'director_id'

t.filter_panel.add_column('year')
t.filter_panel.show()
t.filter_panel.reload()

