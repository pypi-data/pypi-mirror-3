"""uimanager/button-event

A different way to change the popup menu. Here we use the 'button-press-event'
signal of SqlTable



"""
import gtk

def menu_item_cb(menu_item, movie):
    print "Movie %s has %s as director" % (movie, movie.director)

def custom_action_cb(table, event, obj, field_name, menu, treeview):

    if not menu:
        return
    item = gtk.MenuItem("Show director %s" % obj.director)
    item.connect('activate', menu_item_cb, obj )
    table.add_temporary_item(item, menu, separator=True)


t = SqlTable(model.Movie, dbproxy=db)
t.reload()


t.connect('button-press-event', custom_action_cb)
