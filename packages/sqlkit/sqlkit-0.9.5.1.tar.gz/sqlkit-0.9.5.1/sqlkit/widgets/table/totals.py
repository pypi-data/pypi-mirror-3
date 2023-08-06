# Copyright (C) 2005-2010, Sandro Dentella <sandro@e-den.it>
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

.. autoclass:: Totals
   :members: totals, subtotals, add_total, add_break, add_date_break, compute, sum

.. autoclass:: TotalObj
   :members:

"""

from datetime import date, datetime

import gtk
import gobject

from sqlkit import debug as dbg, _
from sqlkit.misc import utils
from sqlkit.widgets.common import sqlwidget

class TotalObj(object):
    """
    A simple class that represents the object holding the totals and a way to represent it

    personalization

    You can change the look of totals inheriting from TotalObj and placing the new class
    as ``class`` attribute of Totals
    """

    _sub_color = 'gray92'
    _total_color = 'gray80'
    _fg_color = 'indianred'

    def __init__(self, fields, sub=True):
        """
        all fields will be initialized to None
        _sub will be set to True for subTotals, to render with different colors
        """
        for name in fields:
            setattr(self, name, None)
        if sub:
            self._color = self._sub_color
        else:
            self._color = self._total_color

    def set_value_and_colors(self, cell, value, field_name):
        """
        set the color cell and possibly background
        """
        if value is not None:
            cell.set_property('markup', "<b><i>%s</i></b>" % (value))
        
        # set color only if we have a value
        if hasattr(self, field_name):
            cell.set_property('foreground', self._fg_color)

    def __getattr__(self, key):
        try:
            object.__getattr__(self, key)
        except AttributeError:
            return None

    
class Totals(gobject.GObject):
    """
    An object whose 'compute' method adds TotalObjets to show
    partial totals/grand totals to a table.
    A TotalObject is inserted each time total_by changes.
    If total_by is a callable, it's evaluated to detect if a partial total
    must be inserted
    """

    __gsignals__ = {
        'computed': (gobject.SIGNAL_RUN_FIRST,
                     gobject.TYPE_NONE,
                     (gobject.TYPE_PYOBJECT,),
                     )
        }

    total_class = TotalObj

    totals = None
    """
    A dict whose keys are the field names for which a total/subtotal is to be computed.
    The values are the totals. It's filled by :meth:`sum` that can be customized.
    """

    subtotals = None
    """
    A dict whose keys are the field names for which a total/subtotal is to be computed
    The values are the subtotals. It's filled by :meth:`sum` that can be customized.
    """
    def __init__(self, table, treeview=None):
        """
        :param table:  the tabe for which a total must be generated
        :param treeview: in case 'table' does not have a treeview, you can specify it.
                       Used when total is made for filter_panel.
        """
        self.__gobject_init__()
        self.table = table
        self.totals = {}
        self._break_field_name = None
        self.subtotals = {}
        self.break_func = None
        self.prev = None
        self.treeview = treeview or table.treeview
        self.table.modelproxy.connect('model-sorted', lambda proxy, model: self.compute())
        self.table.modelproxy.connect('model-pre-sort', self.delete_total_rows)
#        self.table.connect('context-changed', self.update)
#        self.table.connect('records-displayed', self.update)

    def update(self, table, obj=None):

        self.compute()
        
    def add_total(self,  *field_names, **kw):
        """
        Add a total object each time subtotal changes
        
        :param field_names: a list of field_names for which we want a total
        :param quiet: boolean. If True silently fail if the field is not a number
        :param hide_total: boolean. If True gran total will not be shown (only subtotals)
        """
        quiet = kw.get('quiet', False)
        self.hide_total = kw.get('hide_total', False)
        for field_name in field_names:
            if not self.table.get_field_type(field_name) in sqlwidget.NUMBERS:
                self.table.sb(_("Field '%s' is not numeric!!!" % field_name))
                if not quiet:
                    raise NotImplementedError("%s is not a number" % field_name)
                return
            self.totals[field_name] = 0
            self.subtotals[field_name] = 0
        self.compute()
            
    def del_total(self, field_name):
        del self.totals[field_name]

    def add_break(self, field_name, func=None):
        """
        If no ``func`` is provided, a break_func will be setup to insert a subtotal
        each time field_value changes.

        Othewise ``func`` will be set as break_function. Break function must have
        this signature::

           def break_func(obj, field_name, path)

        see ``func_date_*`` is this module for examples
           
        """
        
        if not func:
            def subtotal_diff(obj, path):
                "default subtotal when func not defined"
                try:
                    return getattr(obj, field_name)
                except:
                    return self.table.gui_fields[field_name].clean_value(obj)
            if self.break_func and self._break_field_name == field_name:
                self.break_func = None
            else:
                self.break_func = subtotal_diff
            self._break_field_name = field_name
        else:
            def subtotal_diff(obj, path):
                "default subtotal - func IS defined"
                return func(obj, field_name)
            self.break_func = subtotal_diff
        self.compute()

    def add_date_break(self, field_name, period):
        """
        Set date break period can be: ``day``, ``week``, ``month``, ``quarter``, ``year``
        """
        func = globals()['func_date_same_%s' % period]
        self.add_break(field_name, func)

    def is_different(self, obj, path):

        if self.prev is None:
            self.prev = self.break_func(obj, path)
            return False
        
        if self.prev != self.break_func(obj, path):
            return True
        
        return False

    def initialize(self):
        self.prev = None
        for field_name in self.totals.keys():
            self.totals[field_name]    = 0
            self.subtotals[field_name] = 0

    def sum(self, obj, model, path, iter):
        """
        sum values and store result in :attr:`totals` and :attr:`subtotals`

        :param obj: the obj that should be added. It's an instance of ``table.mapper.class_``
        :param model: the model of the treeview
        :param path: the path at which the obj is
        :param iter: the iter at which the obj is

        To customize the behaviour of total you can just customize this
        method, suppose you want to make it sum flagged objects in table t::

          class BoolTotals(totals.Totals):

              def sum(self, obj, model, path, iter):
                  if obj.flag:
                      for field_name in self.totals.keys():
                          self.totals[field_name]    += getattr(obj, field_name, 0) or 0
                          self.subtotals[field_name] += getattr(obj, field_name, 0) or 0

          t. = SqlTable(...)
          t.totals = BoolTotal(t)
        
        """
        for field_name in self.totals.keys():
            if field_name in self.table.mapper_info:
                value = getattr(obj, field_name, 0)
            else:
                value = self.table.gui_fields[field_name].clean_value(obj)
            self.totals[field_name]    += value or 0
            self.subtotals[field_name] += value or 0

    def reset_subtotals(self):
        for field_name in self.totals:
            self.subtotals[field_name] = 0

    def insert(self, iter, after=None, sub=False):

        tot = self.total_class(self.table.field_list, sub=sub)
        if after:
            try:
                piter = self.table.modelproxy.modelstore.insert_after(iter)
            except TypeError:
                piter = self.table.modelproxy.modelstore.insert_after(None, iter)
                
        else:
            try:
                piter = self.table.modelproxy.modelstore.insert_before(iter)            
            except TypeError:
                piter = self.table.modelproxy.modelstore.insert_before(None, iter)

        self.table.modelproxy.modelstore.set_value(piter, 0, tot)

        newrow = self.table.modelproxy.modelstore[piter]
        return newrow, tot

    def insert_subtotal(self, iter, after=False):

        row, tot = self.insert(iter, after=after, sub=True)
        for field_name in self.totals:
            setattr(tot, field_name, self.subtotals[field_name])
        return row, tot
    
    def insert_total(self, row, after=False):

        if not row:
            
            try:
                # if model[-1] does not exists, no total should be needed...
                # sometime it happens it it tempted anyhow...
                row = self.table.modelproxy.modelstore[-1]
            except IndexError:
                return

        if self.hide_total:
            return row

        row, tot = self.insert(row.iter, after=after, sub=False)
        for field_name in self.totals:
            setattr(tot, field_name, self.totals[field_name])
        return row
    
    def remove(self, iter):
        self.table.modelproxy.modelstore.remove(iter)
        
    def preserve_selection(func):
        def new_func(self):
            self.table.commit_inhibited = True
            selection = self.treeview.get_selection()
            model, rows = selection.get_selected_rows()
            if rows:
                path = rows[0]
                #remember = gtk.TreeRowReference(self.table.modelproxy.modelstore, path)
            func(self)
            if rows:
                #selection.select_path(remember.get_path())
                selection.select_path(path)
            self.table.commit_inhibited = False
        new_func.__doc__ = func.__doc__
        return new_func

    @preserve_selection
    def compute(self):
        """
        Go, add subtotals and total
        """
        if not self.totals.keys():
            return
        self.initialize()
        if not self.table.records:
            return
        self.delete_total_rows()
        self.table.modelproxy.modelstore.foreach(self.foreach_ins_func)

        row = self.insert_total(row=None, after=True)
        if self.break_func:
            self.insert_subtotal(row.iter, after=True if self.hide_total else False)
        self.emit('computed', utils.ObjLike(self.totals))

    def delete_total_rows(self, *args):
        iter_del_list = []
        self.table.modelproxy.modelstore.foreach(self.foreach_del_func, iter_del_list)
        for iter in iter_del_list:
            self.remove(iter)
        
    def foreach_del_func(self, model, path,  iter, iter_del_list):
        """
        
        """
        obj = self.table.modelproxy.modelstore.get_value(iter, 0)
        if isinstance(obj, self.total_class):
            iter_del_list += [iter]
        
    def foreach_ins_func(self, model, path,  iter):
        """
        
        """
        obj = self.table.modelproxy.modelstore.get_value(iter, 0)
        if self.break_func and self.is_different(obj, path):
            self.insert_subtotal(iter)
            self.prev = self.break_func(obj, path)
            self.reset_subtotals()
        if isinstance(obj, self.table.mapper.class_):
            self.sum(obj, model, path, iter)
        
def func_date_same_day(obj, field_name):
    date = getattr(obj, field_name)
    if isinstance(date, datetime):
        return date.date()
    else:
        return date

def func_date_same_week(obj, field_name):
    date = getattr(obj, field_name)
    if date:
        return date.year, getattr(obj, field_name).strftime('%U')
    else:
        return None

def func_date_same_month(obj, field_name):
    date = getattr(obj, field_name)
    if date:
        return date.month, date.year
    else:
        return None

def func_date_same_year(obj, field_name):
    date = getattr(obj, field_name)
    if date:
        return getattr(obj, field_name).year
    else:
        return None

def func_date_same_quarter(obj, field_name):
    date = getattr(obj, field_name)
    if date:
        return date.year, divmod(date.month -1, 3)[0]
    else:
        return None
