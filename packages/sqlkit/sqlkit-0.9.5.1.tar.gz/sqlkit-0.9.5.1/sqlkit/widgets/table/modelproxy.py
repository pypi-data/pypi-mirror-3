# Copyright (C) 2009-2010, Sandro Dentella <sandro@e-den.it>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
===========
ModelProxy
===========

A proxy to the treeview model that can handle both listore and
treemodels and allows to switch easily from one to the other 

A second purpouse is to allow reorderable treeviews (i.e.: those wehere
you can set order by drag&drop) via self.order_store
attribute/function. If position of rows need to be memorized in a visual
way, a field must be set (order_store) that will be reset each time a
new record is added or a row is dragged.

Clearly if that means something at all, entirely depends on the
application. In these cases the order is set in the records currently
handled by the model.

Sorting
=======

A modelproxy can be sorted via it's :attr:`order_by <ModelProxy.order_by`
method. This sorting is done locally as opposed to the sorting done setting
:attr:`SqlWidget.order_by` attribute on the table

Signals
=======

a modelproxy emits signals:

:model-pre-sort: This signal is emitted just before sorting the model. Used to get rid
               of possible "total rows" in the liststore.

:model-sorted: When the model is sorted. Totals listen to this signal
               to be informed they must refresh data

:model-changed: the model has changed the content

.. attribute:: modelstore

   the ListStore or TreeStore for which this ModelProxy is a Proxy.

.. autoclass:: ModelProxy
   :members: __init__, copy, order_by, tree_field_name

"""
import re
from decimal import Decimal

import gtk
import gobject

class ModelProxy(gobject.GObject):
    """
    """

    __gsignals__ = {
        'model-sorted': (gobject.SIGNAL_RUN_FIRST,
                        gobject.TYPE_NONE,
                        (gobject.TYPE_PYOBJECT,)),
        'model-pre-sort': (gobject.SIGNAL_RUN_FIRST,
                        gobject.TYPE_NONE,
                        (gobject.TYPE_PYOBJECT,)),
        'model-changed': (gobject.SIGNAL_RUN_FIRST,
                        gobject.TYPE_NONE,
                        (gobject.TYPE_PYOBJECT,)),
        }
    def __init__(self, master, tree_field_name=None, treeview=None, order_store=None):
        """
        :param master: the sqlwidget this belongs or another modelproxy to copy

        :param tree_field_name: the field_name that will hold parent/child
            relationship. Defaults to None

        :param treeview: the treeview to set the model for or None for later setting.

        :param order_store: the field_name where the path should be stored 
        """
        self.__gobject_init__()
        self.master = master
        self.modelstore = gtk.ListStore(object)
        self._tree_field_name = tree_field_name 
        self.order_store = None
        self._order_list = None
        self._filter_rows = False
        self._check_func = None
        
        self.treeview = treeview
        if treeview:
            treeview.set_model(self.modelstore)

    def copy(self, class_):
        """
        Ceate another ModelProxy of class ``class_`` with the same other values

        :param class_: class of the new ModelProxy, a descendent of ModelProxy. Used when
                       you need to add a function to create a Header (see example 02a)
        """
        m = class_(self.master, tree_field_name=self.tree_field_name, treeview=self.treeview,
                   order_store=self.order_store)
        m.modelstore = self.modelstore
        return m
    
    def _get_tree_field_name(self):

        return self._tree_field_name

    def _set_tree_field_name(self, value):

        if value:
            self.set_treemodel(value)
        else:
            self.set_listmodel()
            
    tree_field_name = property(_get_tree_field_name, _set_tree_field_name)
    """The field on which you want to group rows"""
    
    def update(self):
        """update master view according to self.tree_field_name and self.order_store
        """
        if self.tree_field_name:
            self.set_treemodel(self.tree_field_name)
        else:
            self.set_listmodel()

    def is_tree(self):
        return isinstance(self.modelstore, gtk.TreeStore)
    
    def set_treemodel(self, tree_field_name, tree_order=None):
        """
        change the mode of the Table to a TreeTable, possibly converting the model itself
        (if switching from listmodel or simply changing the tree_field_name).

        For the time being, only TreeTables can be reorderable

        :param tree_field_name: the field_name of the field that will be used to group records
        :param tree_order_field: the field_name where each change in order must be saved
        """
        if isinstance(self.modelstore, gtk.ListStore):
            self.modelstore = gtk.TreeStore(*[self.modelstore.get_column_type(i)
                                             for i in range(self.modelstore.get_n_columns())])
            self._order_id = self.modelstore.connect_after('row-deleted', self.persist_rows_order)

        self._tree_field_name = tree_field_name
        self.treeview.set_reorderable(True)
        self.model_setup()

    def model_setup(self):
        
        self.real_model = self.modelstore
#        self.treeview.set_reorderable(True)
        self.treeview.set_model(self.modelstore)
        self.edited_row_model_path = None
        
    def set_listmodel(self, tree_order=None):
        """
        change the mode of the Table to a TreeTable, possibly converting the model itself
        (if switching from listmodel or simply changing the tree_field_name).

        For the time being, only TreeTables can be reorderable

        :param tree_field_name: the field_name of the field that will be used to group records
        :param tree_order_field: the field_name where each change in order must be saved
        """
        if isinstance(self.modelstore, gtk.TreeStore):
            self.modelstore = gtk.ListStore(*[self.modelstore.get_column_type(i)
                                             for i in range(self.modelstore.get_n_columns())])
            self.real_model = self.modelstore
            #self._order_id = self.modelstore.connect('row-inserted', self.rows_reordered_cb)
                                                           
        self._tree_field_name = None
        self.treeview.set_reorderable(False)
        self.model_setup()
        
    def block_emit_reorder(func, *args, **kw):
        def new_func(self, *args, **kw):
            unblock = False
            if hasattr(self, '_order_id'):
                ## self._order_id is the id of the callback function to 'row-inserted'
                self.modelstore.handler_block(self._order_id)
                unblock = True

            func(self, *args, **kw)
            if unblock:
                self.modelstore.handler_unblock(self._order_id)
                
        new_func.__doc__ = func.__doc__
        return new_func

    @block_emit_reorder
    def fill_model(self, clear=True):
        """
        fill the model according to simplest model type
        """
        self.treeview.set_model(None)
        if clear:
            
            self.modelstore.clear()
            
        if self.tree_field_name:
            self.fill_treemodel()
        else:
            self.fill_listmodel()
            self._sort_model()

        self.treeview.set_model(self.modelstore)
        self.emit('model-changed', self.modelstore)
        
    def fill_listmodel(self):
        for record in self.master.records:
            if self.check_visibility(record):
                self.modelstore.append([record])
        return
        
    def fill_treemodel(self):
        """
        fill the modelstore starting from an empty one and a self.records already complete.
        """
        parents = {}
        for record in self.master.records:
            if not self.check_visibility(record):
                continue
            field_value = getattr(record, self.tree_field_name)
            parent = parents.get(field_value, None)
            if not parent:
                try:
                    header = self.make_header_obj(field_value)
                    parent = parents[field_value] = self.modelstore.append(parent, [header])
                except NotImplementedError:
                    pass
            iter = self.modelstore.append(parent, [record])
            if field_value not in parents:
                parents[field_value] = iter

    def check_visibility(self, obj):
        """
        Return True if the obj should be added to the model of the treeview, False otherwise
        """

        if self._filter_rows and self._check_func:
            return self._check_func(obj)
        return True

    def make_header_obj(self, field_value):
        """
        return a Header obj suitable for header in treemodel mode.
        """
        return NotImplementedError
        #return Header(self.master, self.master.tree_field_name, field_value)

    def reordered_foreach_func(self, model, path, iter):

        obj = model.get_value(iter, 0)
        if obj and isinstance(obj, self.master.mapper.class_):
            setattr(obj, self.order_store, self.get_order_value(path, iter, obj))

    def get_order_value(self, path, iter, obj):

        # add 1 to prevent trimming 1.000 to 1.
        float_repr = [(float(path[i]+1)/10**(i*3)) for i in range(len(path))]
        ret = reduce(lambda x, y: x+y,  float_repr)
        return Decimal(str(ret))

    def persist_rows_order(self, treemodel=None, path=None, iter=None):
        """
        When rows are reordered the new path is written in self.order_store
        that should be a float. To ensure that the database will reload in
        ordered mode a simple algorithm that supposes no more than 1000
        children are present is provided in ``self.get_order_value``. It's
        up to you to refine it for your needs.
        """
        if self.order_store:
            gobject.idle_add(self.modelstore.foreach, self.reordered_foreach_func)
            #self.modelstore.foreach(self.reordered_foreach_func)

    def comp_func(self, obj1, obj2):
        """
        function that compares objects sorting on attributes in self._order_list
        """
        obj1 = obj1[0]
        obj2 = obj2[0]

        fields = self._order_list
        if not fields:
            return 0

        field_name, asc, fkey = self._order_list[0]
        ret = self._cmp(obj1, obj2, field_name, asc, fkey, self._order_list[1:])
        return ret

    def _cmp(self, obj1, obj2, field_name, asc, fkey, more):
        """
        a compare function that can compare on more than one field

        :param obj1/obj2: the objects to compare
        :param field_name: the field_name to sort on
        :param asc: ASCENDING DESC order
        :param fkey: (boolean) it the field is a foreign key
        :param more: other fields to use when field_name is the same

        """
        if hasattr(obj1, field_name):
            v1 = getattr(obj1, field_name)
            v2 = getattr(obj2, field_name)
            if fkey:
                v1 = self.master.gui_fields[field_name].lookup_value(v1)
                v2 = self.master.gui_fields[field_name].lookup_value(v2)
        else:
            v1 = self.master.gui_fields[field_name].clean_value(obj1)
            v2 = self.master.gui_fields[field_name].clean_value(obj2)
            

        if v1 == v2:
            if not more:
                return 0
            else:
                field_name, asc2, fkey2 = more[0]
                return self._cmp(obj1, obj2, field_name, asc2, fkey2, more[1:])


        # v1 an v2 can be None so that a comparison with other values would raise
        # a TypeError
        v1_first = False
        try:
            if v1 < v2:
                v1_first = True
        except TypeError:
            pass

        # Ascending case
        if asc: ## I want None values *before* other values
            if v1_first or v1 is None:  
                return -1
            return 1
        else: # descending, e.g: -date_release
            if v1_first or v1 is None: 
                return 1
            return -1

    def order_by(self, order_list, view='main'):
        """
        set order for the model if it's a ListStore

        :param order_list: fields to use to order, e.g.: +status -description
             to get an ascending ordering on status and descending on description
             implemented just for one attribute
        """

        if order_list == None:
            self._order_list = None
            return
        
        if isinstance(self.modelstore, gtk.TreeStore):
            return
        self._order_list = self._set_order_list(order_list)
        self._sort_model()

    def _sort_model(self, *args):

        if not self._order_list:
            return
        
        self.emit('model-pre-sort', self.modelstore)
        rows = [tuple(r) + (i,) for i, r in enumerate(self.modelstore)]
        if rows:
            rows.sort(cmp=self.comp_func)

            self.modelstore.reorder([r[-1] for r in rows])        
            self.emit('model-sorted', self.modelstore)

    def _set_order_list(self, order_list):

        output = []
        for tk in order_list.split():
            m = re.match('(?P<asc>[+-]?)(?P<field_name>.*)', tk)
            asc, field_name = m.groups()
            fkey = self.master.gui_fields[field_name].fkey
            if asc == '-':
                output += [(field_name, False, fkey)]
            else:
                output += [(field_name, True, fkey)]
        return output
                
    def get_order(self):

        try:
            return self._order_list[0][:2]
        except:
            return None
        
class Header(object):

    def __init__(self, master, field_name, value):

        self.master = master
        value = self.master.gui_fields[field_name].get_human_value(value)
        self.field_name = field_name
        setattr(self, field_name, value)
        
    def __getattribute__(self, name):

        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            return None

    def __str__(self):
        return getattr(self, self.field_name)
