# -*- coding: utf-8 -*-
# Copyright (C) 2008-2009-2010, Sandro Dentella <sandro@e-den.it>
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
.. _fields:

=======
Fields
=======

Mask and Tables display a collection of data that may belong to the database
or not.  Each of the data represented in the GUI that needs to partecipate
to any updating/saving process should have it's own handler that is a Field.

A Field is an entity that knows how to handle a piece of data, be it on the
database (a field_name) or just in the GUI. It's a layer that allows gui
widget to be simpler and easier to interchange. As an example, both varchars
and integers are normally displayed by a gtk.Entry: the entry.get_text()
will retrieve in both cases a string, it's the Field (IntegerField) that
knows how to turn that string into an integer using the
:meth:`Field.clean_value` method. In more complex cases ``clean_value`` can return
data computed from related records.

cthe field knows:

   - if it belongs to the database (attribute ``persistent`` is True) and in
     case how it is defined ( i.e.: sqlalchemy property/column)
   - if it is nullable/editable
   - which widget must be used to represent it (see below, not requested)
   - how to produce a formatted representation of the field.

It provides functions to

   - set/get value
   - get default value (but will not cope with server_side defaults)
   - tell if it changed from the default
   - clean value according to it's logic: i.e. return a value of the correct type
   - validate values (possibly according to other criteria)


The association between a database field and a Field is dome by
:ref:`field_chooser`, but you can force a particular Field when defining the
model class setting the key ``field`` of the column's ``info`` dictionary::

  class MyClass(Base):
      ...
      foo = Column(..., info={'field' : MyField})

A last method is to use :ref:`on_pre_layout hook <on_pre_layout>` that allows
to set ``sqlkit.Fields`` even on non persisted fields.

Relation with the master sqlwidget
----------------------------------

Currently there are a number of operation that require that the field know wich
is the sqlwidget it is acting for. I'd like to loosen this connection in future
but at present it's used in the following situations:

* to keep updated the list of field_widgets
* to get default values (that can be local to a sqlwidget)
* for validation purposes: to issue master.run_hooks and NonNullableException
* FKey: to handle addition of related_obj when cascading policy requires it

In the meanwhile I add master to the Field via set_master() and add a widget
to the Field via set_widget()


Db attributes
-------------

The costructor can be passed a dict of field_attributes

   * field_name: the name of the field
   * nullable: True if field is nullable or False. The related widget will get a background color that
               reflects the fact that it is required (currently yellow). This can be set at any time.
   * editable: True if field is editable or False. The related widget will be set unsensitive. This can
               be set at any time.
   * length: the desired length in chars
   * default: a possible default option
   * type: the python type

   * mapper: defined as None for field that are mapped 
   * table: the SA Table object
   * column: the SA Column object
   * property: the SA Property - if any
   * fkey: the SA ForeignKey or None
   * pkey: True is field is a PRIMARY KEY or False
   
Other attributes
----------------

   * widget:  the widget used to represent it. May be sqlkit.widgets.mask.miniwidget or similar
   * format: the format used to represent the field (numeric or date/time)
   * locale: the locale to use to represent the field (numeric or date/time)
   * DecimalFields also have precision/scale
   * Varchar/TextFields also have blank=True/False (default: False). It determines if an empty string is
     a valid value. Empty strings are differerent from NULL values
     
future
-------
   This should provide a way to set the possible observers

   validation based on the type should live here

   possibly more validation may live here

formatting/locale
-----------------

   see decimal_ to have an intro on formatting numbers

.. _decimal: http://java.sun.com/docs/books/tutorial/i18n/format/decimalFormat.html

.. _field_chooser:

FieldChooser
===============

This class implements a way to determine which Field should be associated to
each field_name in a mapper (used in setup_field_validation so that it can
be easily overwritten).  It's important to understand that it already
receives a gtkwidget from layoutgenerator; that widget has been set by
introspection of the layout description and of the field in the database.

You can overwrite the decision of the field redefining the gui_field on a
derived sqlwidget or passing it as argument (see code snippet 34)::

  class Movie(SqlMask):
      gui_field_mapping = {'date_release' : VarcharField}

  t = Movie(table='movie', dbproxy=db, layout=lay)
  
It's up to the field defined in this way to be able to handle the type of data.
This setting can be used to add field constraints (eg: mail address
validation) or to completely change the widget that represent data.

Widgets
========

A Field does not create a gtk widget to represent data. Layout definition is
normally enought to create the correct GTK widget. If a gtk widget exists
that represent a field, it is handled by a proxy called Miniwidget that
offers a common interface to possbly different gtk widgets. If a MiniWidget
exists the Field will instantiate it and set values thought it. 

A notable exception to this rule is represented by any m2m/o2m relation,
that in the layout is only present as a gtk.Alignment widget to which a
children is added by mask.Widget.

:ref:`Miniwidgets <field-widgets>` for all main types are provided.

Global variables
================

Varchar fields will try to cast an empty value to None unless blank_ok is set
in the field::

    t.gui_field.field_name.blank_ok = True

or globally:

    from sqlkit.widgets.common import fields
    fields.BLANK_OK = True

Default value for BLANK_OK is False.

This is only enforced for NEW records, for already persisted records the default behaviour is
to let it as-is, to prevent a very annoying flood of dialog "do you want to save?" when you
just need to browse some data.


Available Fields
=================

.. autoclass:: Field
   :members: set_widget, set_value, get_value, clear_value, format_value, clean_value,
          has_changed, get_default, set_default, validate, get_human_value, persistent,
          nullable, editable

All other field inherit from Field

.. autoclass:: VarcharField
   :members: blank_ok
   
.. autoclass:: IntegerField
   :members: format

.. autoclass:: FloatField
   :members: format

.. autoclass:: DecimalField
   :members: format

.. autoclass:: TextField
.. autoclass:: DateField
   :members: format

.. autoclass:: TimeField
.. autoclass:: TimeTZField
.. autoclass:: IntervalField
.. autoclass:: DateTimeField
.. autoclass:: DateTimeTZField
.. autoclass:: BooleanField
.. autoclass:: BooleanNullField
.. autoclass:: EnumField
   :members: keys, values, lookup_value
.. autoclass:: ImageField
   :members: base_dir, thumbnail_size, default_size,
             get_value, set_value, clean_value, get_save_path, scale_pixbuf, scale_file,
             create_thumbnail, get_thumbnail, get_thumbnail_path_with_size
   
.. autoclass:: ForeignKeyField
   :members: lookup_value, add_related_object
   
.. autoclass:: CollectionField

.. autofunction:: std_cleanup
"""
import re
import os
import types
import shutil
import warnings
import weakref
from datetime import datetime, time, date, timedelta
from decimal import Decimal

import gobject
import babel
import sqlalchemy
from sqlalchemy.schema import ColumnDefault
from sqlalchemy.orm.interfaces import AttributeExtension
from pkg_resources import parse_version 

from sqlkit import exc, _
from sqlkit.misc import localtimezone
from sqlkit.misc.babel_support import numbers, dates
from sqlkit.db import minspect

from sqlkit.exc import ValidationError, NotHandledField, NotHandledDefault
BLANK_OK = False

class ZoomException(Exception): pass

class SignalEmitter(gobject.GObject):
    """A minimalist gobject used to trace value setting in AttributeExtension
    
    """
    __gsignals__ = {
         'value-set': (gobject.SIGNAL_RUN_FIRST,
                       gobject.TYPE_NONE,
                       (gobject.TYPE_PYOBJECT, gobject.TYPE_PYOBJECT,
                        gobject.TYPE_PYOBJECT, )),
         # 'value-appended': (gobject.SIGNAL_RUN_FIRST,
         #               gobject.TYPE_NONE,
         #               (gobject.TYPE_PYOBJECT, gobject.TYPE_PYOBJECT,
         #                gobject.TYPE_PYOBJECT)),
         # 'value-removed': (gobject.SIGNAL_RUN_FIRST,
         #               gobject.TYPE_NONE,
         #               (gobject.TYPE_PYOBJECT, gobject.TYPE_PYOBJECT,
         #                gobject.TYPE_PYOBJECT)),
         }
    def __init__(self):
        self.__gobject_init__()

    def set_cb(self,  obj, value, oldvalue, initiator):
        "Callback triggered by SQLA events (>= 0.7)"

        self.emit('value-set', value, oldvalue, weakref.ref(obj))
        
class AttrExt(AttributeExtension):
    """An AttributeExtension used to trace value setting. Fields of a mask connect to
    the signal 'value-set' and propagate it. Table's fields don't need to connect as
    they're always tracing object modification via the cell_data_func callback.

    Only used or SQLA version < 0.7

    """
    
    def set(self, state, value, oldvalue, initiator):
        #print 'value-set', state.obj().__class__.__name__, initiator.key, value
        self._sk_emitter.emit('value-set', value, oldvalue, state.obj, )
        return value

    def append(self, state, value, initiator):
        #self._sk_emitter.emit('value-appended', state.obj(), value)
        return value

    def remove(self, state, value, initiator):
        #self._sk_emitter.emit('value-removed', state.obj(), value)
        return value

class FieldChooser(object):

    """here we wrap the gtk widget in a double layer:

        * field for validation
        * widget for edit

    w:           the widget dictionary retuner by Layout
        
    """

    def __init__(self, info, widgets=None, gui_field_mapping=None):
        """    
        info:        a InspectMapper objet
        widgets:     the widget dictionary retuned by Layout
        gui_field_mapping:  a dictionali-like store where to look for custom mapping of
                     field-name and fields. Used when the field cannot be devised
                     from the mapper as the fields are not persisted.
        """
        self.info = info
        self.widgets = widgets or {}
        self.gui_field_mapping = gui_field_mapping or {}

    def get_field(self, field_name, field_attrs=None, def_str=None, test=False):
        """
        return a field

        field_name:  the name of the field in the db
        field_attrs:     the dict for this field as worked out by InspectMapper
        def_str:     the definition string in the layout that determined
                     the gtk.Widget (eg.: c=married, e=first_name)
                     as extracted by layoutgen and set in laygen.fields_in_layout dictionary
        """        

        if field_name in self.gui_field_mapping:
            return self.gui_field_mapping.get(field_name)

        assert field_attrs is not None, \
               "field_name '%s' has no attributes and is not present in gui_fields" % field_name
        col =  field_attrs.get('col', None)
        if col is not None:
            try:
                return col.info['field']
            except (AttributeError, KeyError), e:
                # AttributeError: column (as Label) that don't have .info
                # KeyError when info does not have 'field' key
                pass

        def_str = def_str or ''

        if self.info.is_fkey(field_name):
            return ForeignKeyField

        if self.info.is_loader(field_name):
            return CollectionField
        
        if self.info.is_enum(field_name):
            return EnumField

        if self.info.is_integer(field_name):
            return IntegerField

        if self.info.is_image(field_name):
            return ImageField

        if self.info.is_float(field_name):
            return FloatField

        if self.info.is_numeric(field_name):
            return DecimalField

        if self.info.is_integer(field_name):
            return IntegerField

        if self.info.is_date(field_name):
            return DateField

        if self.info.is_boolean(field_name):
            if self.info.is_nullable(field_name):
                return BooleanNullField
            else:
                return BooleanField
            
        if self.info.is_interval(field_name):
            return IntervalField

        if self.info.is_time(field_name):
            if field_attrs['col'].type.timezone:
                return TimeField
            else:
                return TimeField

        if self.info.is_datetime(field_name):
            if field_attrs['col'].type.timezone:
                return DateTimeTZField
            else:
                return DateTimeField

        if (self.info.is_text(field_name) and not def_str.startswith('e=')) or (def_str.startswith('TX') ):
            return TextField
        
        if self.info.is_string(field_name):
            return VarcharField

        else:
            return VarcharField

#         raise NotHandledField("Field '%s' is not handled in any way: COL_SPEC: %s" %
#                               (field_name, filter_attr['col_spec']))



class Field(gobject.GObject):
    __gsignals__ = {
         'value-set': (gobject.SIGNAL_RUN_FIRST,
                       gobject.TYPE_NONE,
                       (gobject.TYPE_PYOBJECT, gobject.TYPE_PYOBJECT)),
         }
    Widget = None
    default_def_string = 'ae'
    type = None
        
    def __init__(self, field_name, field_attrs=None):
        
        """
        :param field_name:  the name of the field in the db
        :param field_attrs: the dict as worked out by InspectMapper.
                     Can be created by hand: that is useful when field
                     is not mapped in the database. These attributes may be
                     present:

                     :nullable: boolean. If True None is accepted as value
                     :editable: boolean. If True the value can be edited, if 'column'
                                is not passed the field is tuned into not editable
                     :length:   used to determine how many chas are needed to represent it
                     :default:  a possible default value
                     :mapper:   the mapper the field is defined into, if any
                     :pkey:     true if this field is a primary key
                     :fkey:     a sqlalchemy ForeignKey ogject if this field is a foreign key
                     :property: the sqlalchemy property the field has in the mapper
                     :column:   the sqlalchemy column the field maps to
                     :table:    the table the field is defined in, if any
                     
        :param def_str:     the definition string in the layout that determined
                     the gtk.Widget (eg.: c=married, e=first_name)
        :param master:      the sqlkit widget: an instance of SqlMask or SqlTable
        """

        self.__gobject_init__()
        self._ids = {}
        self.field_name = field_name
        self._add_info(field_attrs or {})
        self.initial_value = None

    def set_widget(self, gtkwidget=None, def_str=None, widget=None):
        """
        :param def_str:     the definition string in the layout that determined
                     the gtk.Widget (eg.: c=married, e=first_name)
        :param widget:      the miniwidget to be used. Defaults to class-defined self.Widget
                            the widget can be a string of a Widget derived from
                            ``miniwidget.Widget``
        :param gtkwidget:   the gtk widget to be used (already created by Layout)
        
        """
        from sqlkit.widgets.mask import miniwidgets
        from sqlkit.widgets.table import tablewidgets

        ## when set_widget is used to replace 
        try:
            obj, hid = self._ids['gtkwidget']
            obj.disconnect(hid)
        except KeyError:
            pass
            
        ## widget can be a string in which case it it searched for in
        ## sqlkit.widgets.mask.miniwidgets
        ## this avoids importing miniwidgets at import time and delays it to this function
        if isinstance(widget, basestring):
            Widget = getattr(miniwidgets, widget)

        if def_str and  def_str.startswith('ro='):
            widget = miniwidgets.ReadOnlyWidget
            
        Widget = widget or getattr(miniwidgets, self.Widget)
        if gtkwidget:
            ## used in SqlMask
            self.widget = Widget(gtkwidget, self)
            self._ids['gtkwidget'] = (gtkwidget,
                                      gtkwidget.connect('destroy', self.destroy))
            self.connect('value-set', self.widget.set_value_cb)
        else:
            ### used in SqlTable
            ## tables are inherently already listening to changes in the object
            # via the cell_data_func_cb, so don't need to listen to modifications
            self.widget = tablewidgets.CellWidget(self)

    def destroy(self, widget):

        for obj, hid in self._ids.values():
            obj.disconnect(hid)
        self._ids.clear()

        try:
            del self.widget
            del self.master
        except AttributeError, e:
            pass
            
    def set_master(self, master):
        """
        add a sqlwidget as master of this field. Add a listener to any change to
        the object so that it can be reflected in the widget.

        The master is also used to

          * get defaults
          * validate
          * add related objects
          
        """
        self.master = master
        if self.master.is_table():
            return
        ## make this field listen to modification in the sqlalchemy object (record) so
        ## that any change will be reflected in the UI. Here we implement the mask part
        ## as the table do that inherently via the cell_data_func_cb
        
        if self.persistent:
            emitter = SignalEmitter()
            if parse_version(sqlalchemy.__version__) < parse_version('0.7'):
            
                FieldAttrExt = type(str("attrext_%s" % self.field_name), (AttrExt,),
                                    {'_sk_emitter': emitter})
                extensions = getattr(self.master.mapper.class_, self.field_name).impl.extensions
                found = False
                if extensions is not None:
                    for ext in extensions:
                        if isinstance(ext, AttrExt):
                            found = True
                            emitter = ext._sk_emitter
                            break
                if not found:
                    ext = FieldAttrExt()
                    extensions.append(ext)
                #self._emitter = emitter 
            else:
                from sqlalchemy import event
                # SQLA 0.7 drops support for AttributeExtensions in favor of
                # signals but does not yet implement event.remove as of
                # 0.7.2, so an indirection level is still needed

                instrumented_attr = getattr(self.master.mapper.class_, self.field_name)
                if not hasattr(instrumented_attr, '_sk_emitter'):
                    instrumented_attr._sk_emitter = emitter
                    event.listen(instrumented_attr, 'set', emitter.set_cb)
                else:
                    emitter = getattr(instrumented_attr, '_sk_emitter')

            hid = emitter.connect('value-set', self.value_set_cb)
            self._ids['emitter_value_set'] = (emitter, hid)

    def set_nullable(self, value):
        self._nullable = value
        try:
            self.widget.set_not_null_style(value)
        except AttributeError:
            pass

    def get_nullable(self):
        return self._nullable

    nullable = property(get_nullable, set_nullable)
    
    def set_editable(self, value):
        self._editable = value
        try:
            self.widget.set_editable(value)
        except AttributeError:
            pass

    def get_editable(self):
        return self._editable

    editable = property(get_editable, set_editable)
    
    def _add_info(self, field_attrs):
        """
        read docs in __init__
        """
        self._nullable =  field_attrs.get('nullable', True)  # don't trigger now widget.set_bg()
        self._editable =  field_attrs.get('editable', 'property' in field_attrs and field_attrs['property'] or False)
        self.length   =  field_attrs.get('length', None)
        self.default  =  field_attrs.get('default', None)
        self.mapper   =  field_attrs.get('mapper', None)
        self.pkey     =  field_attrs.get('pkey', None)
        self.fkey     =  field_attrs.get('fkey', None)
        self.property =  field_attrs.get('property', None)
        self.column   =  field_attrs.get('col', None)
        self.table    =  field_attrs.get('table', None)
        if self.pkey:
            self._nullable = False

    def value_set_cb(self, emitter, value, oldvalue, obj):
        """Callback when value is set in the SQLA object"""

        # the signal we received from the record is not emitted when the
        # record is firstly built so we are sure it's not 'initial', we
        # advertise it as 'initial' so that mask won't complain it
        # was changed and ask if it needs saving. It surely does.
        # 2 situation reveal this: 
        # ./demo -i 02, change d.t.current and commit, next forward, we don't
        # want to be prompted to save
        # ./demo 03, right click -> record in mask, change the date in the table
        # and change selected record, we don't want to be prompted to save

        try:
            if obj() is self.master.current and value != oldvalue:
                self.emit('value-set', value, True)
                self.initial_value = value
        except AttributeError, e:
            pass
        
    def set_value(self, value, initial=True, shown=False, obj=None, update_widget=True):
        """
        Set the value
        
        :param value: the value to be set. It will be cleaned.
        :param initial: if True the ``self.initial_value`` is set as. ``self.initial_value``
               is used to know if a field has changed
        :param obj: if passed the attribute is set on the object when the field is set
        :param update_widget: if True (default) the widget that renders the field is set as well.
        """

        value = self.clean_value(value, obj=obj)
        if initial:
            self.initial_value = value
        if obj and self.persistent:
            if not value == getattr(obj, self.field_name):
                # this check shouldn't be needed but I verified that occasionally it would
                # make session.is_modified(obj) to get wrong ideas on the occurred changes
                # ./demo 02 -> ceate a new (empty record)
                # d.t.current.title = None -> d.t.current.date_release = None
                # d.t.session.is_modified(d.t.current)  => True
                setattr(obj, self.field_name, value)
        else:
            self.emit('value-set', value, initial)

    def get_value(self, shown=False):
        """
        Return the current value. Look for it in the widget and returns a cleaned value
        """
        if not hasattr(self, 'widget'):
            return exc.MissingWidget("%s has no defined 'widget' " % self)
        value = self.widget.get_value(shown=shown)
        return self.clean_value(value)

    def clear_value(self):
        """
        sets a value that clears the corresponding widget, can be None or []
        """
        self.set_value(None, initial=True)

    def set_completion(self, regexp):
        pass

    def has_changed(self, verbose=False):
        """
        return True if field has changed after last set
        """
        if not self.editable:
            return False
        try:
            return not self.get_value() == self.initial_value
        except exc.ValidationError:
            # a validation error is a clear sign the values have been changed, but we propabli don't
            # want to cope with them now
            return True
        except exc.NoCurrentObjError, e:
            # if no current Obj, no editing was done
            return False
    
    def get_default(self):
        """
        return the default value for this object
        """
        if hasattr(self, 'master'):
            value = self.master.defaults.get(self.field_name)
        else:
            value = None

        if not value:
            try:
                value = self.default
            except KeyError:
                pass
            if isinstance(value, ColumnDefault):
                if not callable(value.arg) and type(value.arg) == self.type:
                    return value.arg
                else:
                    ## FIXME: I'm not able to handle this now.
                    raise NotHandledDefault
        if not isinstance(value, self.type):
            return
        return value
        
    def set_default(self, obj=None):
        try:
            self.set_value(self.get_default(), obj=obj)
        except NotHandledDefault, e:
            pass
        
    def clean_value(self, value, obj=None):
        """
        return a value of the correct type, if needed parse it with
        locale parsers (numbers, date...)

        :param value: the value to be cleaned (i.e. casted to correct type). It's the
                      attribute of a persisten object or **the object itself** for non
                      persisted fields. I.e.: if you create a custom field to count how many
                      movies has directed each director, the Director instance will be passed
                      as ``value``. 
        :param obj: the object to which the field belongs. It's normally disreguarded but
                    it can be used by special fields (as image fields) to create customized
                    property (e.g.: the save path)

        This function is used while sorting a column 

        """
        return value
   
    def format_value(self, value, format=None):
        """
        return a **string representation** of the value according to current
        locale value is a"cleaned" value

        :param value: the value to be formatted (must already be casted to correct type)
        """
        return value
    
    def validate(self, value, clean=False):
        """
        check if the current value is accepted and call
        :ref:`on_field__validation <on_field__validation>`
        on the master's hook.
        """
        if not clean:
            try:
                value = self.clean_value(value) 

            except Exception, e:
                msg = "Field %s could not validate value '%s': error was: %s" 
                raise exc.ValidationError(_(msg % (field_name, e) ))

        if value is None and not self.nullable and not self.default:
            raise exc.NotNullableFieldError(self.field_name, master=self.master)

        self.master.run_hook('on_field_validation', value, self, field_name=self.field_name)

        return True

    def get_human_value(self, value, format=None):
        """
        return the value or a translation in human readable for foreign key
        """
        return self.format_value(value, format=format)
        
    def _get_persistent(self):
        
        try:
            return self._persistent
        except AttributeError:
            self._persistent = hasattr(self, 'property') and self.property
            return self._persistent

    persistent = property(_get_persistent)
        
    def __repr__(self):
        return "<%s - %s >" % (self.__class__.__name__, self.field_name)

    @classmethod
    def std_cleanup(cls, fn):
        """
        A decorator that will handle standard cases: value is None, is a string
        or is already cleaned.

        This is handy when building new Fields as it allows to keep the
        ``.clean_value`` method as simple as possible, i.e.  no need to check for
        standard cases::

            class CountMovies(fields.IntegerField):
                '''
                A field that counts the movies
                '''
                @fields.std_cleanup
                def clean_value(self, value):
                    ## missing a field_name attribute on obj the object itselt is passed
                    return len(value.movies)

        """
        def new_func(self, value):
            ## standard cleanup: values can
            if isinstance(value, (basestring, types.NoneType, self.type)):
                return super(self.__class__, self).clean_value(value)
            ## custom one
            return fn(self, value)
        new_func.__doc__ = fn.__doc__
        return new_func

class VarcharField(Field):
    """
    The field to represent Strings

    """
    Widget = 'VarcharWidget'
    type = str
    blank_ok = None
    """
    The widget return an epty string on empty values. This variable determines if that value
    will be set NULL or left empty. Regardless of this value the value is left untouched if
    it already exists.
    """
    def __init__(self, *args, **kw):
        Field.__init__(self, *args, **kw)
        self.blank_ok = BLANK_OK
        
    def clean_value(self, value, obj=None):
        if value == '' and not self.blank_ok:
            if not self.initial_value == '':
                value = None
        return value

    def set_value(self, value, initial=True, shown=False, obj=None, update_widget=True):

        if initial:
            self.initial_value = value
        value = self.clean_value(value)

        # if hasattr(self, 'widget') and update_widget:
        #     self.widget.set_value(value or '', initial=initial)

        if obj and self.persistent:
            if not value == getattr(obj, self.field_name):
                setattr(obj, self.field_name, value)
        else:
            self.emit('value-set', value, initial)

    def get_value(self, shown=False):

        value = Field.get_value(self, shown)
        if value == '' and (self.initial_value is None or (
            ## it's very annoying that a db with '' value is turned into None if I don't do anything!
            ## self.blank_ok should only set behaviour of NEW objects
            self.blank_ok is False and not self.initial_value == '')):
            return None
        return value


##### Numbers
class IntegerField(Field):
    """
    The fields to handle interegers
    """
    Widget = 'IntegerWidget'
    type = int
    length = 8

    format = None
    """How to represent integers. Default: '#,###' """
    
    def __init__(self, *args, **kw):
        Field.__init__(self, *args, **kw)
        self.format = "#,###"
        self.locale = babel.default_locale('LC_NUMERIC')
        
    def clean_value(self, value, obj=None):
        if value in (None, ''):
            return None
        else:
            try:
                if isinstance(value, basestring):
                    value = numbers.parse_number(value, locale=self.locale)
                elif isinstance(value, (int, long)):
                    value = int(value)
                else:
                    value = int(value)
            except Exception, e:
                raise exc.ValidationError(str(e))
            return value

    def format_value(self, value, format=None):
        if value is None:
            return ''
        return numbers.format_decimal(value, format=format or self.format, locale=self.locale)
        
    @classmethod
    def std_cleanup(cls, fn):
        """
        A decorator that will handle standard cases: value is None, is a string
        or is already cleaned.

        This is handy when building new Fields as it allows to keep the
        ``.clean_value`` method as simple as possible, i.e.  no need to check for
        standard cases::

            class CountMovies(fields.IntegerField):
                '''
                A field that counts the movies
                '''
                @fields.std_cleanup
                def clean_value(self, value):
                    ## missing a field_name attribute on obj the object itselt is passed
                    return len(value.movies)

        """
        def new_func(self, value):
            ## standard cleanup: values can
            if isinstance(value, (basestring, types.NoneType, self.type, long)):
                return super(self.__class__, self).clean_value(value)
            ## custom one
            return fn(self, value)
        new_func.__doc__ = fn.__doc__
        return new_func
class FloatField(IntegerField):
    """
    The fields to handle floats
    """
    Widget = 'FloatWidget'
    type = float
    length = 10
    
    format = None
    """How to represent integers. Default: None """
    
    def __init__(self, *args, **kw):
        Field.__init__(self, *args, **kw)
        #self.format = "#.###,000"
        self.format = None
        self.locale = babel.default_locale('LC_NUMERIC')
        
    def clean_value(self, value, obj=None):
        if value in (None, ''):
            return None
        else:
            try:
                if isinstance(value, basestring):
                    value = numbers.parse_decimal(value, locale=self.locale)
                elif isinstance(value, float):
                    pass
                else:
                    value = float(value)
            except Exception, e:
                raise exc.ValidationError(e)
            return value
        
    def format_value(self, value, format=None):
        if value is None:
            return ''
        return numbers.format_decimal(value, format=format or self.format, locale=self.locale)
        
class DecimalField(IntegerField):
    """
    The fields to handle Numeric Fields
    """
    Widget = 'DecimalWidget'
    type = Decimal
    length = 10

    scale = 2
    """the number of decimals. Default is desumed by introspection"""

    format = None
    """How to represent integers. Default: '#,###.00' (The number of 0 determined by ``scale`` """
    
    
    def __init__(self, *args, **kw):
        """
        If column is defined precision and scale from column will be used. 
        You need to set precision and scale after the field is created otherwise
        """
        Field.__init__(self, *args, **kw)
        
        if self.column is not None:
            self.precision = self.column.type.precision or 8
            self.scale = self.column.type.scale or 2
        else:
            self.precision = 8
            self.scale = 2
            
        self.format = "#,###.%s" % ('0' * self.scale)
        self.format_f = "%%.%sf" % self.scale
        self.locale = babel.default_locale('LC_NUMERIC')
        
    def clean_value(self, value, obj=None):
        if value in (None, ''):
            return None
        else:
            try:
                if isinstance(value, basestring):
                ## why there's no parse_Decimal in babel?
                    fl = self.format_f % numbers.parse_decimal(value, locale=self.locale)
                    value = Decimal(fl)
                elif isinstance(value, Decimal):
                    pass
                elif isinstance(value, int):
                    value = Decimal(value)
                    #value = self.clean_value(str(value))
                elif isinstance(value, float):
                    fl_str = numbers.format_decimal(value, locale=self.locale)
                    value = self.clean_value(fl_str)
                else:
                    raise exc.ValidationError(_("value is not Decimal nor string: %s" % value))
            except Exception, e:
                raise exc.ValidationError(e)
            return value
        
    def format_value(self, value, format=None):
        if value is None:
            return ''
        return numbers.format_decimal(value, format=format or self.format, locale=self.locale)

    @classmethod
    def std_cleanup(cls, fn):
        """
        A decorator that will handle standard cases: value is None, is a string
        or is already cleaned.

        This is handy when building new Fields as it allows to keep the
        ``.clean_value`` method as simple as possible, i.e.  no need to check for
        standard cases::

            class CountMovies(fields.IntegerField):
                '''
                A field that counts the movies
                '''
                @fields.std_cleanup
                def clean_value(self, value):
                    ## missing a field_name attribute on obj the object itselt is passed
                    return len(value.movies)

        """
        def new_func(self, value):
            ## standard cleanup: values can
            if isinstance(value, (basestring, types.NoneType, self.type, int)):
                return super(self.__class__, self).clean_value(value)
            ## custom one
            return fn(self, value)
        new_func.__doc__ = fn.__doc__
        return new_func
class TextField(VarcharField):
    Widget = 'TextWidget'
    default_def_string = 'TXS'
    type = str

    def set_max_length(self):
        pass

##### Time/Dates
class DateField(Field):
    """
    The fields to handle datets
    """
    Widget = 'DateWidget'
    default_def_string = 'd'
    format = None
    """The format used to represent dates. Default: ``short``"""

    type = date
        
    def __init__(self, *args, **kw):
        Field.__init__(self, *args, **kw)
        self.format = 'short'
        self.locale = babel.default_locale('LC_TIME')
        #if format not in ('short', 'long', 'default', 'medium', 'full'):
        #    pass

    def clean_value(self, value, obj=None):

        if value in (None, ''):
            return None

        try:
            if isinstance(value, basestring):
                value = dates.parse_date(value, locale=self.locale)
            elif isinstance(value, date):
                pass
            else:
                raise exc.ValidationError(_("value is not date nor string: %s" % value))
        except Exception, e:
            raise exc.ValidationError(e)
        return value
    
    def format_value(self, value, format=None):

        if not value:
            return ''

        return dates.format_date(value, format=format or self.format, locale=self.locale)
        
        
class TimeField(DateField):
    """
    The fields to handle times w/o timezone
    """
    Widget = 'TimeWidget'
    default_def_string = 'ae'
    type = time

    def clean_value(self, value, obj=None):

        if value in (None, ''):
            return None

        if isinstance(value, basestring):
            try:
                value = dates.parse_time(value)
            except IndexError, e:
                try:
                    value = dates.parse_time("%s:00" % value)
                except Exception, e:
                    raise exc.ValidationError(e)
        return value
        
    def format_value(self, value, format=None):
        if not value:
            return ''
        
        if not isinstance(value, time):
            value = self.clean_value(value)

        return dates.format_time(value, format=format or self.format, locale=self.locale)

class TimeTZField(TimeField):
    """
    The fields to handle times with timezone
    """
    Widget = 'TimeTZWidget'

    def __init__(self, *args, **kwargs):
        TimeField.__init__(self, *args, **kwargs)
        self.TZ = None
        
    def clean_value(self, value, obj=None):

        if value in (None, ''):
            return None

        if isinstance(value, basestring):
            value = dates.parse_time(value)
        return value
        
    def set_value(self, value, initial=True, shown=False, obj=None, update_widget=True):

        TimeField.set_value(self, value, initial=initial, obj=obj,
                            update_widget=update_widget)
        
        if initial:
            if value:
                self.TZ = value.tzinfo
                self.microsecond = value.microsecond
            else:
                self.TZ = None
                self.microsecond = 0

    def get_value(self, shown=False):

        value = Field.get_value(self, shown)
        if not self.TZ:
            ## Local will return a tzinfo with the timezone of the system
            ## it will be added to bypass the limitation of dateedit
            self.TZ = localtimezone.Local
            self.microsecond = 0

        if value is None:
            return None
        value = time(*[int(i) for i in re.split('[.:]', value)]) 
        return value.replace(tzinfo=self.TZ, microsecond=self.microsecond)

class IntervalField(Field):
    """
    The fields to handle times with interval
    """
    Widget = 'IntervalWidget'
    type = timedelta

class DateTimeField(DateField):
    """
    The fields to handle datetimes w/o timezone
    """
    Widget = 'DateTimeWidget'
    type = datetime

    def __init__(self, *args, **kwargs):
        DateField.__init__(self, *args, **kwargs)
        self.microsecond = 0
        self.second = 0
        
    def clean_value(self, value, add_second=False, add_microsecond=False, obj=None):
        """
        parse and return a clean value (ie: a datetime)
        if add_second/add_microsecond, second and microsecond as found in self.(micro)second
        and stored there by set_value are attached to work around widgets that may not be able 
        (or willing) return seconds and microseconds
        """

        if value in (None, ''):
            return None

        if isinstance(value, basestring):
            tmp_date = re.split('\s+', value.strip())
            try:
                date_value = dates.parse_date(tmp_date[0], locale=self.locale)
            except Exception, e:
                raise exc.ValidationError(_('Wrong date format: %s' % tmp_date[0] ))

            try:
                if len(tmp_date) > 1:
                    time_list = [int(i) for i in re.split('[:.]', tmp_date[1]) ]
                else:
                    time_list = []
                time_value = time(*time_list)

            except Exception, e:
                raise exc.ValidationError(_('Wrong time format' ))

            value = datetime.combine(date_value, time_value)

        if isinstance(value, datetime):
            if add_second:
                value = value.replace(second=self.second)
            if add_microsecond:
                value = value.replace(microsecond=self.microsecond)
            
        return value

    def set_value(self, value, initial=True, shown=False, obj=None, update_widget=True):

        Field.set_value(self, value, initial=initial, obj=obj,
                        update_widget=update_widget)
        
        if initial:
            if value:
                self.TZ = value.tzinfo
                self.microsecond = value.microsecond
                self.second = value.second
            else:
                self.TZ = None
                self.microsecond = 0
                self.second = 0
        
    def format_value(self, value, format=None):

        if not value:
            return ''
        
        return dates.format_datetime(value, format=format or self.format, locale=self.locale)
        
    def get_value(self, shown=False):

        value = Field.get_value(self, shown)

        if value and value.microsecond:
            self.microsecond = value.microsecond
            value = value.replace(microsecond=self.microsecond)

        return value
        
class DateTimeTZField(DateTimeField):
    """
    The fields to handle datetimes with timezone
    """
    Widget = 'DateTimeTZWidget'

    def __init__(self, *args, **kwargs):
        DateTimeField.__init__(self, *args, **kwargs)
        self.TZ = None
        self.microsecond = 0
        
    def clean_value(self, value, add_second=False, add_microsecond=False, obj=None):

        value = DateTimeField.clean_value(self, value, add_second, add_microsecond)

        if not self.TZ:
            ## Local will return a tzinfo with the timezone of the system
            ## it will be added to bypass the limitation of dateedit
            self.TZ = localtimezone.Local
        
        if value:
            if value.tzinfo:
                return value
            else:
                return value.replace(tzinfo=self.TZ)

        return None

    def get_value(self, shown=False):
        """
        Implement a hack around the fact that you normally don't need TZ
        and I don't provide a cell_renderer that gives you the opportunity to change it
        Attach the same timezone as the original data
        """
        value = Field.get_value(self, shown)
        return self.clean_value(value)

##### Boolean
class BooleanField(Field):
    """
    A field to handle booleans that does not allow NULL
    """

    Widget = 'BooleanWidget'
    default_def_string = 'c'
    type = bool

    def clean_value(self, value, obj=None):
        if value is None:
            value = False
        if value not in (True, False):
            msg = "Null value not admittable for field %s" % self.field_name
            raise ValidationError(msg) 
        return value
    
    def clear_value(self):
        ## should I check the default here?
        self.set_value(False)

class BooleanNullField(Field):
    """
    A field to handle booleans that allows NULL
    """

    Widget = 'BooleanNullWidget'
    type = bool

    def clean_value(self, value, obj=None):
        if value not in (True, False, None):
            msg = "Null value not admissable for field %s" % self.field_name
            raise ValidationError(msg) 
        return value
    
class EnumField(Field):
    """
    A field to handle a set of allowed values. You set ``values`` in the
    ``info`` column dict or setting :attr:`values`. Setting info column's
    key ``render`` to 'enum' triggers this field and a widget based on ComboBox.
    It doesn't currently use Sqlalchemy Enum type as it's not yet supported in
    sqlalchemy 0.5. 
    """
    Widget = 'EnumWidget'
    type = (str, int)

    keys = None
    """A list of allowe values in the orederd set by the programmer.
    Used to set the order of the Combo Box"""
    
    values = None
    """A dict: keys are the allowed values, values are te corresponding
    descriptions. It's up to the programmer to set this list appropriately.
    """
    
    def __init__(self, *args, **kw):

        Field.__init__(self, *args, **kw)
        self.values = {}
        values = self.column.info.get('values', [])
        self.keys = [x[0] for x in values]
        for key, value in values:
            self.values[key] = value

    def clean_value(self, value, obj=None):
        """
        Check if value is in the admitted values
        """
        if value in (None, ''):
            return None
        if not value in self.keys:
            raise exc.ValidationError(_("Value '%s' is not accepted") % value)
        return value

    def lookup_value(self, value):
        """
        Return the value to be shown
        """
        return self.values[value]

    def get_value(self, shown=False):

        if not hasattr(self, 'widget'):
            return exc.MissingWidget("%s has no defined 'widget' " % self)
        return self.widget.get_value(shown=shown)

        
class ImageField(VarcharField):
    """
    Imge field suitable for VarcharField that hold an image path and should
    be rendered as image (icon in tables). It's never used when autoloading
    the database schema (no info on the database tells that a string represent an
    image path), it can be forced setting info values on the Column::

      render:         image
      base_dir:       a directory
      thumbnail_size: tuple (width, height)
      default_size:   tuple (width height)
    
    as in::

      image = Column(String(100), info={'render' : 'image', 'base_dir' : '/path/to/images'}
    
    Image field that can create a thumbnail and resize an image into jpeg/png
    format using gtk.gdk.pixbuf* functions
    """
    
    Widget = 'ImageWidget'
    type = str

    thumbnail_size = (50, 50)
    """size of the thumbnail used to render in treeview. Default 50,50. Can be set in
    Column.info as explained above."""

    base_dir = os.getcwd()
    """base directory under which all files will be saved. Default is ``os.getcwd()``
    unless is set at Schema time as shown above.
    :meth:`get_save_path` will use this to create a complete path. This can be set
    when defining the Column as shown above.
    """

    default_size = None
    """If set it must be a tuple (width, height) and all files uploaded will be
    default to these dimentions if bigger.
    """

    def __init__(self, *args, **kw):

        import gtk

        Field.__init__(self, *args, **kw)

        ## set base_dir from Column.info or os.getpwd()
        base_dir = self.column.info.get('base_dir', self.base_dir or os.getcwd())
        base_dir = self.clean_path(base_dir)
        if base_dir and not os.path.isabs(base_dir):
            base_dir = os.path.abspath(os.path.join(os.getcwd(), base_dir))
        self.base_dir = self.clean_path(base_dir)
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)

        self.thumbnail_size = self.column.info.get('thumbnail_size', self.thumbnail_size)
        self.default_size = self.column.info.get('default_size', self.default_size)
        self.image_formats = ["." + x['name'] for x in gtk.gdk.pixbuf_get_formats()] + ['.jpg']
        
    def clean_path(self, path):
        """
        Return a path w/o backslashes as to be used from windows and linux interchangeably

        ``base_dir`` needs to be "cleaned" in this sense.
        
        """
        #return path and re.sub(r"\\", '/', os.path.abspath(path))
        path = path and os.path.normpath(path)  # strip possible ./
        return path and re.sub(r"\\", '/', path)
    
    def get_value(self, shown=False, complete_path=False):
        """
        Return the path to the image

        :param shown: boolean: not meaningful for this field
        :param complete_path: boolean: compose it with base path
        
        """
        if not hasattr(self, 'widget'):
            return exc.MissingWidget("%s has no defined 'widget' " % self)
        value = self.widget.get_value(shown=shown)
        if value and complete_path:
            value = value if os.path.isabs(value) else os.path.join(self.base_dir, value)
        else:
            value = value and re.sub('^%s/?' % self.base_dir, '', value)
        return self.clean_path(value) 
#        return self.clean_path(value) or self.initial_value

    def value_set_cb(self, emitter, value, oldvalue, obj):
        """
        Propagate value set from the attribute extension in the mapped class
        """
        if obj() is self.master.current:
            if value == oldvalue:
                self.set_value(value, initial=False)
            else:
                self.set_value(value, initial=True)

    def set_value(self, value, initial=True, shown=False, obj=None, update_widget=True,
                  new_name=None):
        """
        Set the value and -if needed- copy the image file inside
        :attr:`base_dir` possibly resizing it to :attr:`default_size`. When
        resizing the only possible format is *jpeg* and the name is changed
        accordingly.

        :param value: the value to be set. It will be cleaned.
        :param initial: if True the ``self.initial_value`` is set as. ``self.initial_value``
               is used to know if a field has changed
        :param obj: if passed the attribute is set on the object when the field is set
        :param update_widget: if True (default) the widget that renders the field is set as well.

        """
        if initial:
            # an intial value comes from db and *is* correct by definition
            self.initial_value = value
        else:
            #value = self.clean_value(value) or self.initial_value
            value = self.clean_value(value) 

        if hasattr(self, 'widget'):
            if initial:
                self.widget.copy_file = None # Needed only for table
                
            if update_widget:
                #path = value and os.path.join(self.base_dir, value) or None
                path = value and "%s/%s" % (self.base_dir, value) or None
                self.widget.set_value(path, initial=initial)

            if hasattr(self.widget, 'copy_file') and self.widget.copy_file:
                # Note if it has 'copy_-file' it also has new_filename that may be empty
                save_path = self.get_save_path(name=new_name or self.widget.new_filename or value,
                                               obj=self.master.current)
                if not os.path.splitext(save_path)[1]:
                    save_path += os.path.splitext(self.widget.copy_file)[1]
                if not self.widget.copy_file  == save_path:

                    if self.default_size and self.is_image(self.widget.copy_file):
                        ## I only resize into jpeg format
                        save_path = os.path.splitext(save_path)[0] + '.jpeg'
                        try:
                            self.scale_file(self.widget.copy_file, save_path, *self.default_size)
                        except ZoomException, e:
                            # Don't resave if not needed.
                            shutil.copyfile(self.widget.copy_file, save_path)                            
                    else:
                        shutil.copyfile(self.widget.copy_file, save_path)
                value = self.clean_value(save_path, obj=obj) # It can be changed

        if obj and self.persistent:
            if not value == getattr(obj, self.field_name):
                setattr(obj, self.field_name, value)

    def is_image(self, filename):
        """
        Return if filename seems an image file, depending on file extension.
        """
        ext = os.path.splitext(filename)[1]
        return ext.lower() in self.image_formats
    
    def exists(self, value=None):
        "Return True if the file pointed at value exists"
        value = value or self.get_value()
        if not value:
            return False
        return os.path.exists(os.path.join(self.base_dir, value))

    def clean_value(self, value, obj=None):
        """
        strip self.base_dir from the file if present
        """
        if value in (None, ''):
            return None

        if value:
            return re.sub('^%s/?' % self.base_dir, '', self.get_save_path(value, obj=obj))
        else:
            return None
    
#     def pil_create_thumbnail(self, filename):
#         try:
#             import Image
#         except ImportError:
#             return
#         path = os.path.join(self.base_dir, filename)
#         name, ext = os.path.splitext(filename)
#         i = Image.open(path)
#         i.thumbnail(self.thumbnail_size)
#         self.thumbnail_path = os.path.join(self.base_dir, name + "_thumb" + ext)
#         i.save(self.thumbnail_path)
    
    def get_save_path(self, name=None, obj=None):
        """
        Return a standard save path. You may want to customize it.

        :param name: the name of the file as picked up from the filesystem
                     or the desired new name for the file. :meth:`clean_value`
                     call this also for already save path.
        :param obj: the object. This may be used to work out the path. It's
                     not used by default.
        """
        if not name:
            return None
        obj = obj or self.master.current
        if os.path.isabs(name):
            # if name is relative, it's used in clean_value on already correct values
            # and only base_dir should be added
            name = os.path.basename(name)
        return self.clean_path(os.path.join(self.base_dir, name))

    def scale_pixbuf(self, pixbuf, width=None, height=None):
        """ 
        scale pixbuf image with the same ratio so that it fits into self.w/self.h

        :param pixbuf: the pixbuf to scale
        :param width: the desider width
        :param height: the desider height
        """
        import gtk
        
        pw, ph =  pixbuf.get_width(), pixbuf.get_height()
        ratio = min(width/float(pw), height/float(ph))
        if ratio > 1:
            raise ZoomException("Ratio is > 1 (%s)" % ratio)
        return pixbuf.scale_simple(int(pw*ratio), int(ph*ratio), gtk.gdk.INTERP_BILINEAR)

    def scale_file(self, image_path, dst_path, width, height):
        """
        Scale input file into output file. Keep width/height ratio
        :param image_path: path of the image to resize
        :param dst_path: new name of the image
        :param width: the desired width
        :param height: the desired height
        """
        import gtk
        
        pixbuf = gtk.gdk.pixbuf_new_from_file(image_path)
        pixbuf = self.scale_pixbuf(pixbuf, width, height)
        pixbuf.save(dst_path, 'jpeg')

    def create_thumbnail(self, filename, thumbnail_path=None):
        """
        Create a thumbnail that will be used when rendering images in tables. Uses
        attribute :attr:`thumbnail_size`

        :param filename: the filename to create a thumbnail for
        """
        import gtk

        if not self.is_image(filename):
            return
        path = os.path.join(self.base_dir, filename)
        thumbnail_path = thumbnail_path or self.get_thumbnail_path_with_size(filename)
        pixbuf = gtk.gdk.pixbuf_new_from_file(path)
        pixbuf = self.scale_pixbuf(pixbuf, *self.thumbnail_size)
        pixbuf.save(thumbnail_path, 'jpeg')
    
    def get_thumbnail(self, path=None, complete_path=False):
        """
        Return a thumbnail *path* and create the thumbnail image, if it
        doesn't already exists

        :param path: the path of the image file. If missing it's found using :meth:`get_value`
        :param complete_path: return a complete path. Default is to return the path stripped
               from the :attr:`base_dir`
        """
        ## first build the abs path of the image
        if path and not os.path.isabs(path):
            path = os.path.join(self.base_dir, path)
        path = path or self.get_value(complete_path=True)

        if not os.path.exists(path):
            ## Image does not exists, don't bother with thumbnail
            return
        thumbnail_path = self.get_thumbnail_path_with_size(path)
        
        if not os.path.exists(thumbnail_path):
            self.create_thumbnail(path)

        if complete_path:
            return thumbnail_path
        else:
            return self.clean_value(thumbnail_path, thumbnail=True)

    def get_thumbnail_path_with_size(self, filename):
        """
        Return the thumbnail name for filename using default size. Place the
        thumbnail in a subdir of image dir '.thumbnail' used by
        :meth:`get_thumbnail` and :meth:`create_thumbnail`. The name
        contains the :attr:`thumbail_size` used to generate it.

        :param filename: the complete filename of the image
        """

        path = os.path.join(self.base_dir, filename)
        dir, name = os.path.split(path)
        name, ext = os.path.splitext(name)

        thumbnail_dir = os.path.join(dir, ".thumbnail")
        if not os.path.exists(thumbnail_dir):
            os.mkdir(thumbnail_dir)
        
        thumbnail_path = os.path.join(thumbnail_dir, "%s-%sx%s%s" % (name, self.thumbnail_size[0],
                                                                     self.thumbnail_size[1], ext))
        return self.clean_path(thumbnail_path)

##### Misc
class ForeignKeyField(Field):
    """
    A field to handle foreign keys
    """
    Widget = 'ForeignKeyWidget'
    type = str
    
    def __init__(self, *args, **kwargs):
        Field.__init__(self, *args, **kwargs)

        from sqlkit.db.minspect import get_foreign_info

        self.lookup_values = {}
        self.broken_lookup = False
        self.table, self.column = get_foreign_info(self.fkey, names=False)
        self.table_lookup, self.column_lookup = self.table, self.column

    def lookup_value(self, field_value):
        """
        retrieve the value in a lookup table in case of foreign_key. It means: "given
        the foreign key return a value describing at the best the referenced record". 
        This implies some guessing of the best representation of the record or using
        information given to site-wide database configuration via _sqlkit_table.
        The details of such mechanism are described in :ref:`completion` and :ref:`TableDescr`.
        Since field_value may be incorrectly casted (it is used in completion)
        errors are catched and None is returned (rather than raising an Error)

        """
        from sqlkit.db.utils import tables, get_description, DictLike
        from sqlalchemy import text, select, Table, exceptions

        if field_value is None:
            return ''
        ## broken_lookup is needed just for cases when a referenced column is not unique (FKey)
        # I think this is not regular but fiebird sample database do have such references...
        if self.broken_lookup:
            return field_value
        try:
            return self.lookup_values[self.field_name][field_value]
        except Exception, e:
            descr_fields =  get_description(self.table_lookup)
            format =        get_description(self.table_lookup, attr='format')
            fields = [self.table_lookup.columns[f_name] for f_name in descr_fields]

            sql = select(fields, self.column_lookup == field_value)
            try:
                all = self.table.metadata.bind.execute(sql).fetchall()
            except (exceptions.DBAPIError), e:
                if hasattr(self, 'master'):
                    self.master.sb(e)
                return None

            if len(all) == 0:
                raise exc.LookupValueMissingValue("%s returns no values for '%s': '%s'" % (
                    sql, self.field_name, field_value))
            elif len(all) > 1:
                msg = "%s returns multiple values for '%s': '%s'" % (
                    sql, self.field_name, field_value)
                warnings.warn(msg)
                self.editable = False
                self.broken_lookup = True
                return field_value
                #raise exc.LookupValueMultipleValues()
            else:
                value = format % DictLike(all[0])
                try:
                    self.lookup_values[self.field_name][field_value] = value
                    return value
                except KeyError:
                    self.lookup_values[self.field_name] = {}
                    self.lookup_values[self.field_name][field_value] = value
                    return value

            self.lookup_values[self.field_name][field_value] = value
        return value

    def set_master(self, master):
        Field.set_master(self, master)
        self._props_for_delete_orphan = minspect.get_props_for_delete_orphan(
            master.mapper, self.field_name)
        
    def clean_value(self, value, input_is_fkey=False, obj=None):
        """
        Return a cleaned value (i.e.: the foreign key) or None if no value exists.
        :param input_is_fkey:  If True the text is considered an id, else it's
               considered a 'search' value

        Note that if input_is_fkey=True not cleaning is performed.
        This operation is the opposite of lookup_value().

        Note that clean_value only works if the widget with completion is present.

        """
        if input_is_fkey:
            return value
        
        query = self.widget.completion.compose_select_statement(
            self.widget.completion.query, '=', value)
        ret = query.all()
        #ret = self.master.metadata.bind.execute(sql).fetchone()
        return ret and ret[0][0] or None

    def validate(self, value, clean=False):
        """
        for an fkey field a 'clean' value is an fkey, by definition...
        """
        input_is_fkey = clean

        try:
            value = self.clean_value(value, input_is_fkey=clean)
        except Exception, e:
            msg = "Field %s could not validate value '%s': error was: %s" 
            raise exc.ValidationError(_(msg % (self.field_name, value, e) ))

        if value is None and not self.nullable:
            raise exc.NotNullableFieldError(self.field_name, master=self.master)

        self.master.run_hook('on_field_validation', value, self, field_name=self.field_name)

        return value
        
    def get_value(self, shown=False):

        if not hasattr(self, 'widget'):
            return exc.MissingWidget("%s has no defined 'widget' " % self)
        value = self.widget.get_value(shown)
        ## a shown value is not to be transformed
        if not shown and value == '' and self.initial_value is None:
            return None
        return value

    def get_human_value(self, value, format=None):

        if isinstance(value, (list, tuple)):
            return str([self.lookup_value(v) for v in value])
        return self.lookup_value(value)
    
    def set_value(self, value, initial=True, shown=False, obj=None, update_widget=True):

        if not shown:
            value = self.clean_value(value, input_is_fkey=True)
        if initial:
            self.initial_value = value
        # if hasattr(self, 'widget') and update_widget:
        #     self.widget.set_value(value, shown=shown, initial=initial)

        if value and not initial:
            ## Rationale: See ex_03 (that uses class_=Movie
            # i.e. with definition of relation with backref with delete-orphan). this function
            # is called all the time we enter a record (not just *new* records).

            ## in sqla >= 0.6 therés no way to understand this in an authomatic way, so that
            ## you are supposed to add 'attach_instance' key to Column's info.
            ## read more info in add_related_object's docstring

            for prop in self._props_for_delete_orphan:
                self.add_related_object(prop, value)

        if obj and self.persistent:
            if not value == getattr(obj, self.field_name):
                setattr(obj, self.field_name, value)
        else:
            self.emit('value-set', value, initial)

    def has_changed(self):
        ## special case, when is empty
        if self.initial_value is None and self.widget.get_value(shown=True) == '':
            return False
        
        if hasattr(self.widget, 'real_value') and self.widget.real_value == False:
            return True
        else:
            return Field.has_changed(self)

    def get_default(self):
        """
        return the default value for this object
        """
        ## The only difference from super is that I don't get out if there's a default
        if hasattr(self, 'master'):
            value = self.master.defaults.get(self.field_name)
        else:
            value = None
            
        if not value:
            try:
                value = self.default
            except KeyError:
                pass
            if isinstance(value, ColumnDefault):
                if not callable(value.arg) and type(value.arg) == self.type:
                    return value.arg
                else:
                    ## FIXME: I'm not able to handle this now.
                    raise NotHandledDefault
        ## This has no meaning as self.type has no real meaning in a foreign key
        if not isinstance(value, self.type):
            pass
        return value
        
    def add_related_object(self, prop, key):
        """
        Add an object to fullfill the  constraint on delete-orphan 

        This is not meant to be used directly, it is used by :meth:`set_value`
        If you have a relation with a delete-orphan constraint that would complain
        that is not attached to anybody configure the Column adding in the info
        keyword the ``attach_instance`` key pointing to the property of the relation
        to be added.

        In the demo you can find this example::

          class Movie(Base):
              __tablename__  = 'movie'
              ...
              director_id    = Column(Integer, ForeignKey('director.id'), nullable=False,
                                      info={'attach_instance': 'director'})

          class Director(Base):
              __tablename__ = 'director'
              ...
              movies      = relation('Movie', backref='director', cascade='all, delete-orphan',)

        Attaching a director_id via completion, requires that you attach a director instance as well.

        """
        if not prop:
            return
        # if the backref that requires this is composed, probably things get more difficoult...
        assert len(prop.mapper.primary_key) == 1, "Sorry, sqlkit doesn't cope with " + \
                      "composed primary key in relations with delete-orphan"

        q = self.master.session.query(prop.mapper).autoflush(False)
        obj = q.get(key)
        if self.master.is_mask():
            row_obj = self.master.current
        else:
            row_obj = self.master.get_selected_obj()

        setattr(row_obj, prop.key, obj)
        
class CollectionField(Field):
    """
    A field that manages a collection of objects
    Used in OneToMany or ManyToMany db fields.
    it's default widget is a collectionWidget that uses a SqlTable

    """
    Widget = 'CollectionWidget'

    def __init__(self, *args, **kwargs):
        Field.__init__(self, *args, **kwargs)
        self.initial_value = []

    def value_set_sb(self, *args):
        pass
    def set_widget(self,  gtkwidget=None, def_str=None, widget=None):

        Field.set_widget(self,  gtkwidget=gtkwidget, def_str=def_str, widget=widget)
        self.widget.table.connect('after_commit', self.set_initial_value)
        
    def set_initial_value(self, widget, obj, session):
        """
        after_commit the 'new' initial value is the new value...
        """
        self.initial_value = widget.records

    def get_default(self):
        ## FIXME: is this always correct?
        return None

    def clean_value(self, value, obj=None):
        from copy import copy
        
        if value is None:
            value = []
        return copy(value)

    def set_value(self, value, initial=True, shown=False, obj=None, update_widget=True):

        self.initial_value = self.clean_value(value)
        if value is None:
            value = []
        if hasattr(self, 'widget') and update_widget:
            self.widget.set_value(value, initial=initial)

        if obj and self.persistent:
            setattr(obj, self.field_name, value)


def std_cleanup(fn):
    """
    A decorator that will handle standard cases: value is None, is a string
    or is already cleaned.

    This is handy when building new Fields as it allows to keep the
    ``.clean_value`` method as simple as possible, i.e.  no need to check for
    standard cases::

        class CountMovies(fields.IntegerField):
            '''
            A field that counts the movies
            '''
            @fields.std_cleanup
            def clean_value(self, value):
                ## missing a field_name attribute on obj the object itselt is passed
                return len(value.movies)

    """
    def new_func(self, value, obj=None):
        ## standard cleanup: values can
        if isinstance(value, (basestring, types.NoneType, self.type)) or \
               self.type == int and isinstance(value,long):
            return super(self.__class__, self).clean_value(value)
        ## custom one
        return fn(self, value)
    new_func.__doc__ = fn.__doc__
    return new_func
