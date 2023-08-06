"""uimanager/handling popup menu

You can add entries to the popup. This is just normal gtk.
you just need to know that there exists an action_group names
self.actiongroup_general and a gtk.UIManager called self.ui_manager.


"""

CUSTOM='''
  <popup name="TreePopup">
    <menuitem action="CustomAction" position="top" />
  </popup>
'''

def custom_action_cb(widget):
    print "ok!"

t = SqlTable(model.Movie, dbproxy=db)
view = t.views['main']

view.actiongroup_view.add_actions([
    ('CustomAction', None, 'Tell me sir...', None, None, custom_action_cb),
    ])
view.ui_manager.add_ui_from_string(CUSTOM)

