# Copyright (C) 2005-2006-2007-2008, Sandro Dentella <sandro@e-den.it>
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
================
Layoutgenerator
================

LayoutGenerator
================

build up the layout definition suitable for layout.Layout

Building layout from scratch
----------------------------

In case no layout is passed, a simple layout is built consisting of all
fields vertically packed based on fields in field_list


Passing a  layout
-------------------

In case a layout is passed as argument, the content is parsed to add the
labels and to set the type of widget used to represent the data (using
the mapping in map_types) unless a type is passed in the layout

attributes
----------

``fields_in_layout`` is a dict that maps field_names to widget specification
ie: the key to  be used in widgets dictionary

  * {'first_name': 'e=first_name', 'date': 'd=date', 'year': 'e=year'}

*without any specification*

BUGS
----

At the moment there is redoundancy: here we decide the gtk widget but fields decide
the validation field that on turn set the widget, that on turn pretends a gtkwidget,
this make very diffiocult to add a way to plug in a different rendere for a field.



.. Reference to other tables
.. ---------------------------
.. 
.. A name of a field can also be of the form: table.field_name, in which case
.. the table is reflected to get the type of the column, to adjust for the
.. proper widget representation

"""
import re
import datetime
import decimal

from sqlalchemy import *

import sqlkit as sk
from sqlkit import debug as dbg
from sqlkit.layout import widgets

for mod in ('m2m', 'm2o', 'o2m', 'o2o'):
    widgets.register_alias(widgets.Alignment, mod)

class FkEdit(widgets.LWidget):
    gtkClass = 'FkEntry'
            
class IntervalEdit(widgets.LWidget):
    gtkClass = 'IntervalEdit'
            
class GreedyTreeView(widgets.LWidget):
    gtkClass = 'GreedyTreeView'

widgets.register(FkEdit, 'fk')
widgets.register(IntervalEdit, 'delta')
widgets.register(GreedyTreeView, 'TV', force=True)

class LayoutGenerator (object):
    map_types = {
        datetime.datetime     : 'dt',
        datetime.date         : 'd',
        datetime.time         : 'ae', 
        datetime.timedelta    : 'delta', 
        bool                  : 'c',
        int                   : 'ae',
        float                 : 'ae',
        str                   : 'ae',
        unicode               : 'ae',
        decimal.Decimal       : 'ae',
        }
    
    def __init__ (self, master, naked=False, lay=None):
        """
        fields: an InspectMapper object
        """
        self.master = master

        if lay:
            lay = re.sub('#.*\n','', lay)

        self.loaders = {}
        self.fields_in_layout = {}  # {'first_name': 'e=first_name', 'date': 'd=date'}

        if self.master.is_mask():
            if not lay:
                lay = self.create_default_layout()
            self._look_for_explicit(lay)
            self.layout = self._parse_and_complete(lay)
            
        else:
            self.layout = lay or self.create_for_table()

        if not naked:
            self._add_default_buttons()
            
    def _parse_and_complete(self, lay):
        """parse the layout and substitute all field_name with:

            L=field_name mod=field_name

        where mod is the appropriate modifier ([edc])
        field_name must be preceded and followed by a space or newline
        """
        p = re.compile(r"""^(\s*#.+)""", re.MULTILINE)
        lay = p.sub('', lay)   # strip any comment

#        (?<![\S%{=]\b)   # \b bound of a string <![{] is not preceded by {
#                     # this is to excude  {N   (container + flags)

        p2 = re.compile(r"""
        (?<!\S)                # next row must not match if preceded by any str
                               # %string is a qualifier for notebooks
                               # {N is for notebooks and so on
        ( ((?P<mod>[a-zA-Z0-9]+)(?P<equal>=+))? # a possible modifier
        (?P<field>[a-z_0-9A-Z\.]+))  # the field + a possible table (table.field)
        (?![-])               # the row above is only matched if not followed
                               # by - o = (b=gtk-save-as *must not* match)
        (?P<spec>:[-<>.,a-zA-Z\d]*)?
        (?P<end>\b)
        """, re.VERBOSE | re.MULTILINE)

        return p2.sub(self._sub, lay)
    
    def _sub(self, m):
        """called from inside regexp
        """
        field_name = m.group('field')
        mod = m.group('mod')

        if not self.needs_parsing(field_name, mod):
            return m.group(0)

        ## check if we defined already a Field via gui_field_mapping

        if hasattr(self.master, 'gui_field_mapping'):
            Field = self.master.gui_field_mapping.get(field_name, None)
        else:
            Field = None
            
        widget = mod or self.get_widget(field_name, Field)
        spec = m.group('spec') or ''
        
        if self.master.is_loader(field_name):
            self.loaders[field_name] = spec

        if not spec:
            spec = self.create_spec(field_name, Field, widget)
        
        self.fields_in_layout[field_name] = "%s=%s" % (self.get_edit_string(widget), field_name)

        if m.group('equal') == '==':
            ## implement the request to provide a way prevent layoutgenerator from creating the label
            ## == inhibits creation of label.
            return m.group(0).replace('==', '=')
        
        return "L=%s %s=%s%s" % (field_name, widget, field_name, spec)

    def needs_parsing(self, field_name, mod):

        #         if field_name not in self.master.field_list or mod in ('L','le', 'm2m', 'o2m','m2o'):
        #             return m.group(0)
    
        needs = False
        if mod in ('L','le', 'm2m', 'o2m','m2o'):
            needs = False

        elif field_name in self.master.field_list:
            needs = True

        elif hasattr(self.master, 'gui_field_mapping') and field_name in self.master.gui_field_mapping:
            needs = True

        return needs
        
    def get_edit_string(self, mod):
        """
        return the real modifier that handle editing
        """
        if mod in ('ae'):
            return 'e'
        if mod in ('aC'):
            return 'C'
        if mod in ('TXS'):
            return 'TX'
        else:
            return mod
        
        
    def get_widget(self, field_name, Field=None):
        """
        choose appropriate widget to represent this field
        check if a particular field was already defined in gui_fields
        """
        ## check if we defined already a Field via gui_field_mapping
        if Field:
            widget_str = getattr(Field, 'default_def_string')
            if widget_str:
                return widget_str
            

        #self.used_field_dict[field_name] = 

        if self.master.is_fkey(field_name):
            ## ForeignKey for foreign key
            return "fk"

        if self.master.is_loader(field_name):
            return "m2m"

        if self.master.is_image(field_name):
            return 'img'
        
        if self.master.is_enum(field_name):
            return 'aC'
        
        ftype = self.master.get_field_type(field_name)
        widget = self.map_types[ftype]
        
        if self.master.is_text(field_name):
            widget = 'TXS'
        return widget

    def create_spec(self, field_name, Field, widget_mod):
        """
        create a spec string that decides how long en entry must be
        reflects fom db
        :param field_name: the field name for which we want to create reasonable specs
        :param Field: an optional fields.Field instance used to device length
        :param widget_mod: the widget_modifier used to 
        """
        if widget_mod == 'TXS':
            # self.master.is_text() is not reliable at this stage as uses info
            # of self.field_in_layout that are not available
            # if TXT= is imposed in layout definition (as opposed to model definition)
            return ":250.100"
        try:
            length = self.master.mapper_info.fields[field_name]['length']
            col_spec = self.master.mapper_info.fields[field_name]['col_spec'] or ''
            db_type  = self.master.mapper_info.fields[field_name]['db_type']
        except AttributeError:
            length = Field.length if hasattr(Field, 'length') else None
            
        if self.master.is_fkey(field_name) or self.master.is_loader(field_name):
            ### FIXME: should I set the length of the foreign key?
            return ''
        
        if not length:
            if self.master.is_integer(field_name):
                return ":8"
            elif self.master.is_float(field_name):
                return ":8"
            elif self.master.is_number(field_name):
                return ":10"
            m = re.search('VARCHAR.(\d+).', col_spec)
            if m:
                length = int(m.group(1))
        if length:
            if self.master.is_image(field_name):
                return ''
            ## really long field should not eat up all the space
            ## (but you can override this by hand!...)
            if length > 30:
                length = 30
            ## now alignment: this will ensure it will grow
            ##  if more space is given to the window via rezising
            spec = ":%s" % length
            if length> 20:
                spec += "-"
            #  else:
            #      spec += "<"
            return spec
        return ''
                    
        
    def register(self, field_name):
        """regiter field_name as a field_name of a table to be found and reflected
        field_name must be of the form table.field_name
        """

        p = re.compile("""
           ([-_A-Za-z0-9]+)   # table name
           \.                 # separator
           (\S+)             # field_name
        """, re.VERBOSE)
        m = p.search(field_name)
        if not m:
            #dbg.write("%s not of the form table.field" % field_name )
            return (field_name, None, None)
        table_name = m.group(1)
        #dbg.write('table_name:', table_name)
        tbl_field_name = m.group(2)
        engine = self.master.mapper_info.mapper.local_table.engine
        table = Table(table_name, engine, autoload=True)
        t1 = type(table.c[tbl_field_name].type)
        col_spec = table.c[tbl_field_name].type.compile(dialect=engine.dialect)
        t = self.master.mapper_info.fields.pytype[t1]
        return (tbl_field_name, t, col_spec)

    def _add_default_buttons (self):
        # a 'naked' mask is a mask w/o buttons. Maybe buttons are define by the
        # programmer inside the layout, maybe are not desired

        self.layout = """
        {V.header }
        {A.external { %s}}
        sb=StBar
        """ % (self.layout)
#        {A.external {S {p { %s}}}}
    
    def create_for_table(self):
        """
        A minimal layout for nested sqlwidget
        """
        
        lay = """
          TVS=tree
          {A.icons {H.icons %s}}          
        """ % (self.master.icons)

        return lay

    def _look_for_explicit(self, lay):
        """
        Look for names that represent loaders, if any parse it for:

          * rows          (eg: m2m=actors:5)
          * field_list    (eg: m2m=actors:5:first_name,last_name)

        set it in self.loaders['movies'] = {'rows': 5, 'field_list': 'first_name,last_name'}
        """

        pat = re.compile("""
          (?P<mod>[a-zA-Z0-9]+)=        # the modifier, but not the = sign
          (?P<field_name>[a-zA-Z0-9_\.]+)         # the possible loader:
                                              # genre  genre.movies
          (:(?P<spec>\d*))?                   # number of rows for the table
          (:(?P<field_list>[\w,]*))?             # number of rows for the table
          $
        """, re.VERBOSE | re.MULTILINE)

        for token in lay.split():
            m = pat.match(token)
            if m:
                field_name     = m.group('field_name')  # to be verified
                mod        = m.group('mod')
                spec       = m.group('spec')
                field_list = m.group('field_list')

                if field_name not in self.master.field_list:
                    continue

                if self.master.is_loader(field_name):
                    self.loaders[field_name] = {}
                    if spec:
                        self.loaders[field_name]['rows'] = int(spec)
                    if field_list:
                        self.loaders[field_name]['field_list'] = field_list
                    
                self.fields_in_layout[field_name] = "%s=%s" % (
                    self.get_edit_string(mod), field_name)

    def create_default_layout(self, rows=20):
        """
        Create a default layout.
        Don't display more that 20 attributes in a column.

        """
        n_fields = len(self.master.field_list)        
        columns = int(n_fields / rows) + 1
        lay = []
        for i in range(0, n_fields, columns):
            lay += [" ".join(self.master.field_list[i:i+columns])]

        return "\n".join(lay)

