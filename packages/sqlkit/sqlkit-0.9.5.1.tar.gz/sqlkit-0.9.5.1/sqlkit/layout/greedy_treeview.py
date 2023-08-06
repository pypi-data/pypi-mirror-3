"""
A TreeView which gives as size_request the sum of the width requests of its
columns

"""

import gtk
import gobject

class GreedyTreeView(gtk.TreeView):
    __gtype_name__ = 'GreedyTreeView'
   
    def __init__(self, *args):
        gtk.TreeView.__init__(self, *args)

    def do_size_request(self, requisition):
        
        treeview = self
        gtk.TreeView.do_size_request(self, requisition)
#        print "width would be", requisition.width



        model = treeview.get_model()
        try:
            rows_number = len(model)
        except:
            return
        
        columns = treeview.get_columns()
        titles = [column.get_title() for column in columns]
        
        widths = []
        
        width_known = True
        
        for column_index in range(len(titles)):
            column = columns[column_index]
            cell_renderers = column.get_cell_renderers()
            renderers_widths = []
            # We have 3 possibilities:
            # 1) the renderer has a fixed width (the member "fixed_width" is set in
            #    table.py): we just take this as its width
            # 2) the renderer has a variable size and its criterion for populating
            #    is set in table.py: then, it also has a member 'cells_data_func',
            #    which contain informations about the criterion, and we use it to
            #    populate and ask get_size()
            # 3) the renderer wasn't set in table.py: we just take a constant size.
            
            for renderer in cell_renderers:
                if hasattr(renderer, 'fixed_width') and renderer.fixed_width:
                    renderers_widths.append(renderer.get_size(treeview, None)[2])
                elif hasattr(column, 'cells_data_func'):
                # We'll have to check with all values that populate the column.
                    renderer_func = None
                    for cell_func in column.cells_data_func:
                        if cell_func[0] == renderer:
                            renderer_func = cell_func[1]
                            renderer_func_data = cell_func[2:]
                            break
                    if renderer_func:
                        # This will be the minimum (for non populated columns).
                        max_width = 30
                        for row_index in range(rows_number):
                            iter = model.get_iter(row_index)
                            renderer_func(column, renderer, model, iter, *renderer_func_data)
                            if gobject.type_is_a(renderer, gtk.CellRendererText):
                                ellipsize = renderer.get_property('ellipsize')
                                renderer.set_property('ellipsize', False)
                            width = renderer.get_size(treeview, None)[2]
                            if gobject.type_is_a(renderer, gtk.CellRendererText):
                                # Put things back in order.
                                renderer.set_property('ellipsize', ellipsize)
                            max_width = max(max_width, width)
                        renderers_widths.append(max_width)
                    else:
                        # The renderer was not found!
                        width_known = False
                        break
                else:
                    # Don't know how to populate the renderer!                   
                    width_known = False
                    break
                    
            top_widget = column.get_property('widget')
            if top_widget:
                top_width = top_widget.get_allocation().width
            else:
                top_width = 0

            expected_width = sum(renderers_widths)
            expected_width += len(cell_renderers)*treeview.style_get_property('horizontal-separator')
            widths.append(max(expected_width, top_width) + 4)   # FIXME: clarify this 4
    
#            print "column", column.get_title()
 #           print "renderers", cell_renderers
  #          if hasattr(cell_renderers[0], 'lenght'):
   #             print "lenght", cell_renderers[0].lenght
    #        print "widths", renderers_widths
#        print "widths", widths
        
        if width_known:
            total_desired_width = sum(widths)
        else:
            total_desired_width = treeview.size_request()[0]

        # If we happened to mismatch because of missing introspection, let's
        # trust in gtk... 
        requisition.width = max(total_desired_width, requisition.width)
#        print "instead, it could be", total_desired_width, "... it is", requisition.width
