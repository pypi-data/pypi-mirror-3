"""hooks/on_init with buttons

In this example, on_init is used to configure callback on button 'b=ciao'
that is only present in the mask that will pop up if you right click on a row

Registering a hook
------------------

note that here we have registered the hook rather than passing it to the
sqlwidget. The advantage is that it will be used by *any* widget that is
created. Of course you should be carefull in using this feature as any
contraints will be enforced in any sqlwidget of that table.

When registering a hook or a layout you can mask it with a nick and use
layout_nick when calling it.

"""
from sqlkit.db.utils import get_differences
from sqlkit.db import defaults

class Hooks(object):

    def on_init(self, sqlwidget):

        sqlwidget.completions.director_id.group_by = 'nation'
        sqlwidget.gui_fields.year.format = '#'
        
        if sqlwidget.is_mask():
            button = sqlwidget.widgets['b=ciao']
            button.connect('clicked', self.button_clicked_cb)

    def button_clicked_cb(self, widget):
        print "Ciao, mondo"


LAYOUT = """
   title
   year
   director_id
   b=ciao -
"""
defaults.register_hook('movie', Hooks)
defaults.register_layout('movie', LAYOUT)


t = SqlTable(model.Movie, dbproxy=db, order_by='title')
t.reload()

# clean up to prevent conflicts with following examplesx
defaults.unregister_hook('movie', )
defaults.unregister_layout('movie',)

