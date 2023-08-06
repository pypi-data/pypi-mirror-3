# Copyright (C) 2005 Sandro Dentella. All rights reserved.
# e-mail: sandro@e-den.it
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software 
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

import re
import os

import gtk
import gobject

from sqlkit import _
from sqlkit import debug as  dbg
from sqlkit.layout.greedy_treeview import GreedyTreeView

class IdentifierAlreadyPresent: pass

info = {}
class LWidget(object):
    #__metaclass__ = LogTheMethods
    #logMatch = "position*"
    
    gtkClass = None
    transpose = {'w' : 'width_request',
                 'h' : 'height_request'
                 }
    class_properties = {'visible' : True}
    class_pack_properties  = {'y-options' : '0'}

    def __init__(self, el_def, pos, container, elements, layout):
        ## update info for this class
        # print "Lwidget: %s %s" % (el_def,  self.gtkClass)
#         if self.gtkClass == 'GtkAlignment':
#             dbg.show_caller(sfilter='elements')

        self.el_def = el_def
        assert layout is not None
        self.layout = layout
        self.lw = {}
        self.container_flag = container
        self.properties = {}
        self.pack_properties = {}
        # By default, widgets do not expand vertically. Those who do can be
        # recognized (and set) by this attribute being True
        self.v_expand = False
        # used to specify order in properties
        self.ordered_properties = []
        if self.gtkClass:
            self.properties.update(LWidget.class_properties)
            self.pack_properties.update(LWidget.class_pack_properties)
            
        self.properties.update(self.class_properties)

        self._parse_cell_def(el_def)
        self.lw.update( {   ## lw : layout widget
           'container' : container,
           'el_def'    : el_def,
           'gtkClass'  : self.gtkClass,
           'children_list' : [],
        } )
        self.position(pos)
        self.pos = pos
        self.elements = elements
        self._labels_and_tips_from_info()
        #dbg.write('class_specific', type(self))
        self._class_specific()
#         if re.match('GtkEventBox', self.gtkClass):
#             dbg.write('ok')            
        self._set_dimentions()
        #dbg.debug("elements[%s] = %s (%s)" % (self.lw['el_key'],
        #                                     self,elements.keys()) )
        elements[self.lw['el_key']] = self

    def position(self, (row, col)):
        ## ask the class of the container which are the pack_properties
        ## apart from Table. Table has position changing, the others pack
        ## widgets as they arrive. I tried with classmethod for Table w/ no luck
        if self.container_flag in ('T'):                  
            self.pack_properties.update( {
                'left_attach'       : col,
                'top_attach'        : row,
                'right_attach'      : col+1,
                'bottom_attach'     : row+1,
                })
        else:
            self.pack_properties.update(
                _W[self.container_flag].class_pack_properties)

    def _debug_pos(self):
        p = self.pack_properties
        if self.container_flag == 'T':
            return "pos: %s : %s" % ((p['top_attach'],p['left_attach']),
                                     (p['bottom_attach'],p['right_attach']))
        else:
            return ''

    def _parse_cell_def(self, el_def):
        pattern = re.compile(r"""
          (?:(?P<flag>\w+)=)?      # ignore if passed the full string
          (?P<val>[^/:<>]*)        # value
          (?:/(?P<var>[^:]+))?     # variable
          (?:(?::(?P<w>[\d]*))?      # width
          \.?
          (?P<h>-?[\d]+)?)?            # height
          (?P<align>[-<>])?         # align, a < or a > at the end of the string
        """, re.VERBOSE)
        match = pattern.search(el_def)
        self.class_flag = match.group("flag")
        self.val = match.group("val")
        self.var = match.group("var")
        self.w = match.group("w")
        self.h = match.group("h")
        self.align = match.group("align")
        #dbg.write("el: %s w=%s h=%s align=%s-" % (el_def,self.w,self.h, self.align))
        #print  "_parse_cell_def: el: %s var=%s val=%s h=%s align=%s" % (
        #    el_def,self.var,self.val, self.h, self.align)
        #print match.groups()
        if not self.var:
            ## radiobutton use self.val as 'group'
            if not re.search("GtkRadioButton",self.gtkClass):
                self.var = self.val

        ## let's set a reasonable key. Strip any width info
        # not sure If I should put all Containers
        cont_pat = "Gtk(Frame|Table|HBox|VBox|Notebook)"
        if not re.search(cont_pat,self.gtkClass):
            self.lw['el_key'] = re.sub('(:.*)|[-<>]$','',el_def)
        else:
            self.lw['el_key'] = re.sub('[-<>|=]$','',el_def)

        ### gtk-stock?
#         if re.match('gtk-', self.val) and not self.gtkClass == 'GtkImage':
        if gtk.icon_factory_lookup_default(self.val) and not self.gtkClass == 'GtkImage':
            if re.match('GtkToolButton', self.gtkClass):
                self.properties['stock_id'] = re.sub('\..+','',self.val)
                self.properties['label'] = None
            elif re.match('GtkButton', self.gtkClass):
                self.properties['label'] = _(re.sub('\..+','',self.val))
                #dbg.write(self.properties['label'])
                self.properties['use-stock'] = True
            else:
                self.properties['use-stock'] = True


    def _labels_and_tips_from_info(self):
        """
        set possible label and tip 
        """

        if not self.class_flag:
            return

        label, tip = self.get_label_and_tip()
        
        if label:
            self.val = label

        if tip:
            self.properties['tooltip_text'] = tip

    def get_label_and_tip(self):
        """
        keys can be mapped to labels in 3 ways:

          1. via a label_map local to the layout (shared with all nested layout)
          2. via a global info dictionary
          3. via gettext

        1. is attempted first, failing that 2. is attempted.
        The resulting string is anyhow passed via gettext.
        The aim is to allow to use per-table (meaning database table) translation from a
        name to the relative label. Names can normally be similar between tables.
        """

        name = self.val
        key = "%s=%s" % (self.class_flag, name)

        details = self.layout.label_map.get(key, None) or info.get(key, None)
        if not details:
            details = self.layout.label_map.get(name, None) or info.get(name, None)

        if details:
            return details
        else:
            return None, None


    def _set_dimentions(self):
        """Give a meaning to dimentions for this object"""
        ## width
        if self.w and  'w' in self.transpose:
            name = self.transpose['w']
            self.properties[name] = self.w
            #self.pack_properties['x_options'] = 'shrink'
        ##  'height'
        if self.h and  'h' in self.transpose:
            name = self.transpose['h']
            self.properties[name] = self.h
            
    def rowspan(self):
        if self.lw['container'] in ('T'):
            self.pack_properties['bottom_attach'] += 1
#         else:
#             dbg.warning("Span available only for Table qui: %s" % \
#                       self.lw['container'])

    def colspan(self):
        if self.lw['container'] in ('T'):
            self.pack_properties['right_attach'] += 1
#         else:
#             dbg.write("Span available only for Table qui: %s" % self.lw['container'])


    def _class_specific(self):
        pass
    
    ### Real pack
    def xml(self, ContGtkClass=None):
        return "%s\n%s" % (self._widget_xml(),
                           self._packing_xml(self.pack_properties,ContGtkClass))

    def create(self):
        """ Create the wdget """
        #dbg.write(self.gtkClass)
        #print dbg.dshow(self.properties)
        self.gtkWdg = gobject.new(gobject.type_from_name(self.gtkClass))
        # **self.properties
        for p, val in self.properties.iteritems():
            try:
                self.gtkWdg.set_property(p, val)
            except:
                pass
                #dbg.write("Fail prop %s for %s" % (p, self.gtkClass))

        return self.gtkWdg
                          
    def _packing_xml(self, pack_properties, ContGtkClass):
        # no packing if adding with 'addto'. In that case ContGtkClass
        # is not defined
        if not ContGtkClass:
            return ""

        allowed_pack_properties = ()
        for i in gtk.container_class_list_child_properties(ContGtkClass):
            allowed_pack_properties += (i.name,)

        xml = ["<packing>"]
        for key, value in pack_properties.iteritems():
            ## tabs label are child of notebook but of a type that
            ## is not returned by container_class... function above
            if (key == 'type' and ContGtkClass == 'GtkNotebook') \
                   or key.replace('_','-') in allowed_pack_properties:
                 xml.append('  <property name="%s">%s</property>' % (key, value))
        xml.append("</packing>")
       
        return "\n".join(xml)
    
    def _widget_xml(self):
        # If a children is v_expandable, the parent becomes too.
        if 'children_list' in self.lw and self.lw['children_list']:
            if True in [child.v_expand for child in self.lw['children_list']]:
                self.make_v_expandable()
    
        xml = ['<object class="%(gtkClass)s" id="%(el_key)s">' % self.lw]
        inner_xml = []
        # write properties with order before
        extra_text = ""
        for key in self.ordered_properties:
            value = self.properties[key]
            if key in self.transpose:
                pass
                #print key, self.transpose[key]
            if key in ('text', 'label'):
                extra_text = ' translatable="yes"'
                if value == '':
                    value = None
            else:
                extra_text = ""
                
            if value:
                inner_xml.append('<property name="%s"%s>%s</property>' %\
                                (key, extra_text, value))
        
        # now write everything else
        extra_text = ""
        for item, value in self.properties.iteritems():
            if item not in self.ordered_properties:
                if item in self.transpose:
                    item = self.transpose[item]
                if item in ('text', 'label'):
                    extra_text = ' translatable="yes"'
                else:
                    extra_text = ""
                    
                if value is not None:
                    inner_xml.append('<property name="%s"%s>%s</property>' %\
                                     (item, extra_text, value))

        children = self._children_xml()
        if children:
            inner_xml.append(children)
        xml.append(self._offset_txt("\n".join(inner_xml), 2))
        xml.append("</object>")
        return "\n".join(xml)

    def _children_xml(self):
        # this is significant only for LContainer
        return None

    def _offset_txt(self, txt, amount):
        ## offset text to get a prettier xml
        p = re.compile("^", re.MULTILINE)
        return p.sub(' ' * amount, txt)

    def make_v_expandable(self):
        """Teach a widget it must expand (vertically); it can be because it has
        a viewing benefit (e.g: a Treeview) or because a child of it has.
        """
        if self.v_expand:
            return
        self.v_expand = True
        # FIXME: (how?!) this expands horizontally if parent is a HBox
        self.pack_properties.update({'expand' : True})
        self.pack_properties.update({'y-options' : 'expand | fill'})


    def __str__(self):
        return "<%s: %s >" % (self.__class__.__name__, self.el_def)
    def __repr__(self):
        return "<%s: %s >" % (self.__class__.__name__, self.el_def)
class LContainer(LWidget):
    # the difference with LWidget is it has children
    # and the el_def is not written in the layout but created on the fly
    # (Layout._create_container_label). We use it as label
    class_pack_properties  = {'y-options' : 'fill|expand'}

    def __init__(self, el_def, pos, container, children_list=None, elements=None, layout=None):
        LWidget.__init__(self, el_def, pos, container, elements=elements, layout=layout)
        ## the children
        self.lw['children_list'] = children_list
        #self.properties['label'] = el_def
        
    def _children_xml(self):
        txt = ''
        try: 
            for obj in self.lw['children_list']:
                child = self._offset_txt(obj.xml(self.gtkClass), 4)
                txt += "\n<child>\n%s\n</child> <!-- closes %s in %s -->\n" % (
                    child, obj.lw['el_key'], obj.lw['container'])
        except:
            pass
        return txt
    def create(self, visible=None):
        """ Create the wdget """
        if visible is not None:
            self.properties['visible'] = visible
            
        #dbg.write(self.gtkClass)
        self.gtkWdg = gobject.new(gobject.type_from_name(self.gtkClass),
                          **self.properties)

        #dbg.write(gtkWdg)
        self.add_children(self.gtkWdg)
        return self.gtkWdg
                          
    def add_children(self, gtkWdg):

        if not self.lw['children_list']:
            return
        
        for obj in self.lw['children_list']:
            #dbg.write("gtkWdg", gtkWdg, obj.gtkClass)
            child = obj.create()
            pack_props = self.clean_pack_properties(obj.pack_properties, gtkWdg)
            
            if self.gtkClass not in ('GtkTable'):
                #dbg.write('%s.add(%s, %s)' %(gtkWdg, child, pack_props ))
                gtkWdg.add(child)
                for p, val in pack_props.iteritems():
                    #dbg.write("%s.set_property(%s, %s)" % (gtkWdg, p, val))
                    setattr(gtkWdg, p, val)
            if self.gtkClass == 'GtkTable':
                P = pack_props
                #dbg.write("pack_props", P, obj.pack_properties)
                gtkWdg.attach(child,
                           P['left_attach'],
                           P['right_attach'],
                           P['top_attach'],
                           P['bottom_attach'],
                           )

        return 
    def clean_pack_properties(self, pack_props, gtkWdg):
        return pack_props
#         dbg.write(gtkWdg, gtkWdg.name)
#         dbg.write(gtk.container_class_list_child_properties(gtkWdg))
#         props = [p.name for p in gtk.container_class_list_child_properties(gtkWdg)]
#         dbg.write(props)
#         ko = []
#         for p in pack_props:
#             if p not in props:
#                 ko += [p]
#         for p in ko:
#             del pack_props[p]
#         dbg.write(pack_props)
#         return pack_props

class AlignmentEntry(LContainer):
    gtkClass = 'GtkAlignment'

    def __init__(self,  el_def, pos, container, children_list=None, elements={}, layout=None):
        el_def = el_def.replace('ae=','A=')
        super(LContainer, self).__init__(el_def, pos, container, elements=elements, layout=layout)
        ## prepare the names...

        entry_str   = "e=%s" % (el_def.replace('A=',''))
        wdg = Entry(entry_str,(0,0),    'A', elements=elements, layout=layout)
        self.lw['children_list'] = [ wdg ]
        if self.align == '-':
            self.properties['xscale'] = 1
        else:
            self.properties['xscale'] = 0

        if self.align == '>':
            self.properties['xalign'] = 1
        else:
            self.properties['xalign'] = 0

    def _class_specific(self):
        self.pack_properties.update({
            'x_options' : 'expand|fill',
            })

    def _get_w(self):
        return -1
    def _set_w(self, value):
        ## when setting the with of an ae object we just want to set the width of the entry
        return
    w = property(_get_w, _set_w )

class Entry(LWidget):
    gtkClass = 'GtkEntry'
    transpose = {
        'w' : 'width_chars',
        }
#     def _class_specific(self):

#         if self.w:
#             self.properties['max-length'] = self.w

            
class DateEdit(LWidget):
    gtkClass = 'DateEdit'
    ## this widget is provided by dateedit module
            
class ImageWidget(LWidget):
    gtkClass = 'ImageWidget'
    ## this widget is provided by image module
    class_properties = {
        'image' : None,
        }
            
class DateTimeEdit(LWidget):
    gtkClass = 'DateTimeEdit'
    ## this widget is provided by dateedit module
    class_properties = {
        'time' : None,
        'lower-hour' : 10,
        'upper-hour' : 23,
        'show-time' : None,
        'use-24h-format' : True
        }
            
class Calendar(LWidget):
    # TODO: add a constructor to pass dates in a friendly way
    gtkClass = 'GtkCalendar'
    def _class_specific(self):
        self.pack_properties.update({'y_options': ""})
    #class_properties = {
        #'visible'     : True,
        #'day'     : 7,
        #'month'     : 3,
        #'year'     : 1963,
        #}
    

class TreeView(LWidget):
    gtkClass = 'GreedyTreeView'
    transpose = {
        'w' : 'width_request',
        'h' : 'height_request',
        }
    class_properties = {
        'width_request'  : '-1',
        'height_request'  : '-1',
        }

    def _class_specific(self):
        self.make_v_expandable()
        
class TextView(LWidget):
    gtkClass = 'GtkTextView'
    transpose = {
        'w' : 'width_request',
        'h' : 'height_request',
        }
    class_properties = {
        'width_request'  : '280',
        'height_request'  : '100',
        }
    def _class_specific(self):
        self.make_v_expandable()


class Statusbar(LWidget):
    gtkClass = 'GtkStatusbar'
    
    def _class_specific(self):
        if self.container_flag == "T":
            self.pack_properties.update({'y_options': ''})
        elif self.container_flag == "V":
            self.pack_properties.update({'pack_type': 'GTK_PACK_END'})


class Label(LWidget):
    gtkClass = 'GtkLabel'
    transpose = {
        'w' : 'width_chars',
        }
    def _class_specific(self):
        self.properties.update({
            'xalign' : '1',
            'label'  : _(self.val).replace('_',' ') + ':',
            'xpad'   : 10,
            'use-markup' : True,
            })
        self.pack_properties.update({
            'y_options' : 'fill',
            'x_options' : 'fill',
            })
        if self.align:
            #dbg.debug("SELF ALIGN for ", self.lw['el_key'])
            if self.align in '<':
                #dbg.debug("""properties['xalign'] = 0""")
                self.properties['xalign'] = 0
            else:
                self.properties['xalign'] = 1

class LabelFill(LWidget):
    gtkClass = 'GtkLabel'
    
    def _class_specific(self):
        self.properties.update({
            'xalign' : '0',
            'label'  : _(self.val),
            'xpad'   : 10,
            })
        self.pack_properties.update({
            'y_options' : 'expand|shrink|fill',
            })

class NotebookLabel(Label):
    """This is for the tab of a notebook"""
    gtkClass = 'GtkLabel'
    
    # def _class_specific(self):
    #     ## must overwrite any other info
    #     self.pack_properties = {
    #         'type' : 'tab',
    #         }

class FrameLabel(Label):
    """This is for the tab of a notebook"""
    gtkClass = 'GtkLabel'
    class_properties = {
        'xpad' : 5,
        }    
    def _class_specific(self):
        ## must overwrite any other info
        self.pack_properties = {
            'type' : 'label_item',
            }

class Button(LWidget):
    gtkClass = 'GtkButton'
#     transpose = {
#         'w' : 'width_chars',
#         }
    class_pack_properties = {
        'expand' : False,
        'fill'   : True,
        }

    def _class_specific(self):
        self.properties.update({
            'xalign' : '0',
            'label'  : _(re.sub('\..+','',self.val))
            })        
        
        self.pack_properties.update({'y_options': ""})


class ToolButton(LWidget):
    gtkClass = 'GtkToolButton'

    def _class_specific(self):
        #if re.match("gtk-",self.val):
        if gtk.icon_factory_lookup_default(self.val):
            del self.properties['label'] 
            #self.properties['stock_id'] = self.val

class RadioButton(Button):
    gtkClass = 'GtkRadioButton'
    def _class_specific(self):
        if self.var:
            ## this puts this radioButton in the same group as the radiobutton
            ## written after the '/'
            self.properties['group'] = 'r=' + self.var

class ToggleButton(Button):
    gtkClass = 'GtkToggleButton'
    
class CheckButton(Button):
    gtkClass = 'GtkCheckButton'
    def _class_specific(self):
        self.properties['label'] = ''

class LinkButton(LWidget):
    gtkClass = 'GtkLinkButton'
#     transpose = {
#         'w' : 'width_chars',
#         }
    class_pack_properties = {
        'expand' : False,
        'fill'   : True,
        }

    def _class_specific(self):
        self.properties.update({
            'xalign' : '0',
            'label'  : _(re.sub('\..+','',self.val))
            })        
        
        self.pack_properties.update({'y_options': ""})


class ProgressBar(LWidget):
    gtkClass = 'GtkProgressBar'

class ComboBox(Entry):
    gtkClass = 'GtkComboBox'
    transpose = {
        'w' : 'width_request',
        }
    def _class_specific(self):
        self.pack_properties.update({
            'x_options' : 'fill',
            })

class AlignmentComboBox(LContainer):
    gtkClass = 'GtkAlignment'

    def __init__(self,  el_def, pos, container, children_list=None, elements={}, layout=None):
        el_def = el_def.replace('aC=','A=')
        super(LContainer, self).__init__(el_def, pos, container, elements=elements, layout=layout)
        ## prepare the names...

        entry_str   = "C=%s" % (el_def.replace('A=',''))
        #print "ENTRY_STR", entry_str
        ## and create the children
        #print "EventLabel elements: ", elements.keys()
        wdg = ComboBox(entry_str,(0,0),    'A', elements=elements, layout=layout)
        self.lw['children_list'] = [ wdg ]
        if self.align == '-':
            self.properties['xscale'] = 1
        else:
            self.properties['xscale'] = 0

        if self.align == '>':
            self.properties['xalign'] = 1
        else:
            self.properties['xalign'] = 0

    def _class_specific(self):
        self.pack_properties.update({
            'x_options' : 'expand|fill',
            })

    def _get_w(self):
        return -1
    def _set_w(self, value):
        ## when setting the with of an ae object we just want to set the width of the entry
        return
    w = property(_get_w, _set_w )

class ComboBoxEntry(Entry):
    gtkClass = 'GtkComboBoxEntry'

class SpinButton(LContainer):
    gtkClass = 'GtkSpinButton'
    class_properties = {
        "can_focus"     : True,
        "climb_rate"    : 1,
        "digits"        : 0,
        "numeric"       : True,
        "update_policy" : 'GTK_UPDATE_ALWAYS',
        "snap_to_ticks" : False,
        "wrap"          : False,
#        "adjustment"    : '0 0 1000 1 10 0',
        }

class ToolSpinButton(LContainer):
    gtkClass = 'GtkToolItem'
    def __init__(self, el_def, pos, container, elements, layout=None):
        el_def = el_def.replace('ts=', 'ti=')
        #super(LContainer, self).__init__(el_def, pos, container=container, elements=elements, layout=layout)
        super(ToolSpinButton, self).__init__(el_def, pos, container=container, elements=elements, layout=layout)
        ## if spinbutton in toolbar, we need to encapsulate in a ToolItem
        spin_def = el_def.replace('ti=','s=')
        spin = SpinButton("%s" % (spin_def), (0,0), 'ti', elements=elements, layout=layout)
        self.lw['children_list'] = [ spin  ]
        #self.el_def = "ti=%s" % (self.var)
            
class Image(LWidget):
    gtkClass = 'GtkImage'
    def _class_specific(self):
        ## self.var is probably the name of a image file
        ## let's check, look for it and set it with a full path
        #if self.var.startswith('gtk-'):
        if gtk.icon_factory_lookup_default(self.var):
            self.properties['icon_name'] = self.var
            self.properties['icon_size'] = self.w
            self.w = None
            self.properties.pop('width_request', None)
        else:
            cdir = os.getcwd()
            filename = os.path.join(cdir,self.var)
            if os.path.exists(filename) and os.path.isfile(filename):
                self.properties['pixbuf'] = filename

class Window(LContainer):
    gtkClass = 'GtkWindow'
    ## secondo me questo non dovrebbe essere necessario
    class_pack_properties  = {  }
    class_properties = {
        'visible' :            True,
        'title' :              'window1',
        'type' :               'GTK_WINDOW_TOPLEVEL',
        'window_position' :    'GTK_WIN_POS_NONE',
        'modal' :              False,
        'resizable' :          True,
        'destroy_with_parent' : False,
        'decorated' :          True,
        'skip_taskbar_hint' :  False,
        'skip_pager_hint' :    False,
        'type_hint' :          'GDK_WINDOW_TYPE_HINT_NORMAL',
        'gravity' :            'GDK_GRAVITY_NORTH_WEST',
        }    

    def __init__(self, *args, **kw):
        LContainer.__init__(self, *args, **kw)

    def _packing_xml(self, packing_info, ContGtkClass):
        return ''

class Table(LContainer):
    gtkClass = 'GtkTable'
    class_pack_properties = {
        'homogeneous' : False,
#        'expand'       : True,
        'y_options' : 'shrink',
#        'y_options' : 'expand|fill',
        'x_options' : 'shrink',
        }
    #def _class_specific(self):
        #self.pack_properties.update({"y_options": ""})

class VBox(LContainer):
    gtkClass = 'GtkVBox'
    class_pack_properties = {
        'padding' : '0',
        'expand'  : False,
        'fill'    : False,
        }
    
    class_properties = {
        'homogeneous' : False,
        'spacing' : 0,
        }
    
class HBox(VBox):
    gtkClass = 'GtkHBox'
    
class Layout(LContainer):
    gtkClass = 'GtkLayout'
    
class Fixed(LContainer):
    gtkClass = 'GtkFixed'
    
class ScrolledWindow(LContainer):
    gtkClass = 'GtkScrolledWindow'
    def _class_specific(self):
        self.properties.update({
            'hscrollbar_policy' : 'GTK_POLICY_AUTOMATIC',
            'vscrollbar_policy' : 'GTK_POLICY_AUTOMATIC',
            'shadow_type'       : 'GTK_SHADOW_IN',

        })

        self.pack_properties.update({
            'expand' : True,
            'fill' : True,
            #'y_options' : 'GTK_EXPAND|GTK_FILL',
            #'y_options' : 'GTK_EXPAND|GTK_FILL',
            })
    

class Notebook(LContainer):
    gtkClass = 'GtkNotebook'
    def _class_specific(self):
        self.make_v_expandable()

    def _children_xml(self):
        txt = ''
        try: 
            for obj in self.lw['children_list']:
                ## incorrect: it would fail f the only sun of a tab is a Label!!!
                child_type = 'type="tab"' if obj.gtkClass == 'GtkLabel' else ''
                    
                child = self._offset_txt(obj.xml(self.gtkClass), 4)
                txt += "\n<child %s>\n%s\n</child> <!-- closes %s in %s -->\n" % (
                    child_type, child, obj.lw['el_key'], obj.lw['container'])
        except:
            pass
        return txt

class VPaned(LContainer):
    gtkClass = 'GtkVPaned'
    class_pack_properties = {
        'resize' : False,
        }
    def __init__(self, el_def, pos, container, children_list=None, elements=None, layout=None):
                 
        msg = "%s cannot have more that 2 children (now: %s)" % (self.gtkClass, children_list)
        assert len(children_list) <= 2, msg
        LWidget.__init__(self, el_def, pos, container, elements=elements, layout=layout)

        ## the children
        self.lw['children_list'] = children_list
    
    def _class_specific(self):
        self.make_v_expandable()

class HPaned(VPaned):
    gtkClass = 'GtkHPaned'
    #class_pack_properties = VPaned.class_pack_properties

class DrawingArea(LWidget):
    gtkClass = 'GtkDrawingArea'
    
class HandleBox(LContainer):
    gtkClass = 'GtkHandleBox'
    
class Expander(VPaned):
    gtkClass = 'GtkExpander'
    class_properties = {
        'expanded' : False,
        'border_width' : 3,
        }
    def _class_specific(self):
        label = self.el_def.replace('X.','').replace('_',' ')
        self.properties['label'] = label
    
class ViewPort(LContainer):
    gtkClass = 'GtkViewport'
    
class Frame(LContainer):
    # a frame conta
    gtkClass = 'GtkFrame'
    class_properties = {
        'label_xalign' : 0,
        'border_width' : 6,
        'label_yalign' : 0.5,
        'shadow_type' : 'GTK_SHADOW_ETCHED_IN',
        }
    
class FrameWithLabel(LContainer):
    # a frame conta
    gtkClass = 'GtkFrame'
    class_properties = {
        'label_xalign' : 0,
        'label_yalign' : 0.5,
        'border_width' : 6,
        'shadow_type' : 'GTK_SHADOW_ETCHED_IN',
        }
    
    def __init__(self,  el_def, pos, container, children_list=[], elements={}, layout=None):
        super(LContainer, self).__init__(el_def, pos, container, elements, layout=layout)
        ## prepare the names...
        al_str = "A=%s" % (self.val.replace('F','') )
        ## and create the children. We pass the child over to Alignment
        alignment = Alignment(al_str,(0,0),    'F' ,
                              children_list=children_list, elements=elements, layout=layout)
#         fl_def = "fl=%s" % self.val.replace('F','')
#         frame_label = FrameLabel(fl_def, (0,0), 'F', elements=elements, layout=layout) 
#         self.lw['children_list'] = [ alignment, frame_label ]
        self.lw['children_list'] = [ alignment ]
        ## correct the parent_container of the child
        alignment.lw['container_flag'] = 'A'
        
class Alignment(LContainer):
    gtkClass = 'GtkAlignment'
    class_properties = {
        'xalign' : 0.5,
        'yalign' : 0,
        'xscale' : 1,
        'yscale' : 1,
        'top_padding' : 4,
        'bottom_padding' : 4,
        'left_padding' : 8,
        'right_padding' : 4,
        }
    
class EventBox(LContainer):
    gtkClass = 'GtkEventBox'
    class_properties = {
        'visible_window'  : True,
        'above_child' : False,
        }
    def _class_specific(self):
        ## not executed frm EventLabel
        pass

class EventLabel(LContainer):
    gtkClass = 'GtkEventBox'

    def __init__(self,  el_def, pos, container, children_list=[], elements={}, layout=None):
        #dbg.write("EventLabel ", el_def)
        el_def = el_def.replace('L=','E=')
        super(LContainer, self).__init__(el_def, pos, container, elements=elements, layout=layout)
        ## prepare the names...

        lbl_str   = "l=%s:.%s" % (el_def.replace('E=',''), self.w or '')
        ## and create the children
        #print "EventLabel elements: ", elements.keys()
        label = Label(lbl_str,(0,0),    'E', elements=elements, layout=layout)
        self.lw['children_list'] = [ label ]
        
    def _class_specific(self):
        self.pack_properties.update({
            'x_options' : 'fill',
            })


class ComboLE(LContainer):
    # it'a HBox/VBox with a label and an entry
    gtkClass = 'GtkVBox'

    def __init__(self,  el_def, pos, container, children_list=[], elements=None, layout=None):
        super(ComboLE, self).__init__(el_def, pos, container, elements=elements, layout=layout)
        ## prepare the names...
        lbl_str   = "E=%s:%s%s" % (self.val, self.w or '', self.align or '')
        entry_str = "e=%s:%s%s" % (self.var, self.h or '', self.align or '')
        #dbg.debug(entry_str, lbl_str, self.w, self.h)
        ## and create the children
        label = EventLabel(lbl_str,(0,0),    'V', elements=elements, layout=layout)
        entry = Entry(entry_str,(0,1),  'V', elements=elements, layout=layout)
        self.lw['children_list'] = [ label, entry ]
        ### w and h are there only to propagate to label & entry
        self.w = None
        self.h = None
        try:
            del self.properties['height_request']
        except:
            pass
    
    def _class_specific(self):
        self.pack_properties.update({"y_options": ""})

class ScrolledTreeView(LContainer):
    gtkClass = 'GtkScrolledWindow'

    def __init__(self,  el_def, pos, container, children_list=[], elements={}, layout=None):
        el_def = el_def.replace('TVS=','S=')
        super(LContainer, self).__init__(el_def, pos, container, elements, layout=layout)
        ## prepare the names...
        tree = "TV=%s:%s.%s" % (self.val, self.h or '', self.w or '')

        ## and create the children
        new = TreeView(tree,(0,0),    'S', elements, layout=layout)
        self.lw['children_list'] = [ new  ]
    def _class_specific(self):
        self.pack_properties.update({
            'expand' : True,
            'fill' : True,
            })
        

class ScrolledLayout(ScrolledWindow):
    gtkClass = 'GtkScrolledWindow'

    def __init__(self,  el_def, pos, container, children_list=[], elements={}, layout=None):
        el_def = el_def.replace('LS=', 'S=')
        super(LContainer, self).__init__(el_def, pos, container=container, elements=elements, layout=layout)
        ## prepare the names...
        tree = "Lay=%s:%s.%s" % (self.val, self.h or '', self.w or '')

        ## and create the children
        new = Layout(tree,(0,0),    'S', elements=elements, layout=layout)
        self.lw['children_list'] = [ new  ]
    def _class_specific(self):
        self.pack_properties.update({
            'expand' : True,
            'fill' : True,
            })
        

class ScrolledTextView(ScrolledWindow):
    gtkClass = 'GtkScrolledWindow'

    def __init__(self,  el_def, pos, container, children_list=[], elements={}, layout=None):
        el_def = el_def.replace('TXS=','S=')
        #super(LContainer, self).__init__(el_def, pos, container, elements)
        ScrolledWindow.__init__(self, el_def, pos, container=container, elements=elements, layout=layout)
        ## prepare the names...
        tree = "TX=%s:%s.%s" % (el_def.replace('S=',''), self.h or '', self.w or '')

        ## and create the children
        new = TextView(tree,(0,0),    'S', elements=elements, layout=layout)
        self.lw['children_list'] = [ new  ]
        
class ScrolledDrawingArea(ScrolledWindow):
    gtkClass = 'GtkScrolledWindow'

    def __init__(self,  el_def, pos, container, children_list=[], elements={}, layout=None):
        el_def = el_def.replace('daS=','S=')
        #super(LContainer, self).__init__(el_def, pos, container, elements)
        ScrolledWindow.__init__(self, el_def, pos, container=container, elements=elements, layout=layout)
        ## prepare the names...
        wdg = "da=%s:%s.%s" % (self.val, self.h or '', self.w or '')
        #dbg.write('wdg', wdg)
        ## and create the children
        new = DrawingArea(wdg,(0,0),    'S', elements=elements, layout=layout)
        self.lw['children_list'] = [ new  ]
        

class MenuBar(LContainer):
    gtkClass = 'GtkMenuBar'
    class_pack_properties = {
        'y_options' : 'fill',
        'x_options' : 'fill',
        }
    def _class_specific(self):
        if self.container_flag == "T":
            #self.pack_properties.update({'y_options': ''})
            self.pack_properties.update(
                {'y_options': 'fill',
                'x_options' : 'fill',
                 }
                )

class Menu(LContainer):
    gtkClass = 'GtkMenu'
    # I don't mean to fill it up with MenuItems. I'll 

class ToolItem(LContainer):
    gtkClass = 'GtkToolItem'

class MenuItem(LContainer):
    gtkClass = 'GtkMenuItem'
    parent = 'm'

    def __init__(self,  el_def, pos, container, children_list=[], elements={}, layout=None):
        super(MenuItem, self).__init__(el_def, pos, container, [], elements, layout=layout)
        #print "MENU: " + el_def
        ## prepare the names...
        menu = "M=%s" % (self.val)

        ## and create the children
        new = Menu(menu,(0,0), self.parent, children_list=[], elements=elements, layout=layout)
        #print "new menu ", new, menu, self.parent
        self.lw['children_list'] = [ new  ]

    def _class_specific(self):
        self.properties['label'] = _(self.val)
        #self.properties['use_underline'] = True
        
        # specify that we want write label before use_underline
        #self.ordered_properties = ["label", "use_underline"]
        
    def _children_xml(self):
        txt = ''
        try: 
            for obj in self.lw['children_list']:
                ## incorrect: it would fail f the only sun of a tab is a Label!!!
                child_type = 'type="submenu"' if obj.gtkClass == 'GtkMenu' else ''
                    
                child = self._offset_txt(obj.xml(self.gtkClass), 4)
                txt += "\n<child %s>\n%s\n</child> <!-- closes %s in %s -->\n" % (
                    child_type, child, obj.lw['el_key'], obj.lw['container'])
        except:
            pass
        return txt

#         for f in self.lw['children_list']:
#             dbg.debug("%s %s" % (self, self.lw['children_list']))

class MenuToolButton(MenuItem):
    gtkClass = 'GtkMenuToolButton'
    parent = 'tm'
#     transpose = {'var' : 'label',
#                  }
#     # I don't mean to fill it up with MenuItems. I'll 

class Toolbar(LContainer):
    gtkClass = 'GtkToolbar'
    # fixme; transpose does nos seem to work...
    transpose = {'width' : 'width_request',
                 'height' : 'height_request'
                 }
    def _class_specific(self):
        if self.container_flag == "T":
            self.pack_properties.update({'y_options': ''})


class ColorSelection(LWidget):
    gtkClass = 'GtkColorSelection'
    
class ColorButton(LWidget):
    gtkClass = 'GtkColorButton'

##### Widgets list
_W = {
    'l'   : Label,
    'lf'  : LabelFill,
    'ro'  : LabelFill,
    'L'   : EventLabel,
    'nl'  : NotebookLabel,
    'fl'  : FrameLabel,
    'e'   : Entry,
    'ae'  : AlignmentEntry,
    'aC'  : AlignmentComboBox,
    'd'   : DateEdit,
    'dt'  : DateTimeEdit,
    'da'  : DrawingArea,
    'i'   : Image,
    'img' : ImageWidget,
    'b'   : Button,
    'lb'   : LinkButton,
    'r'   : RadioButton,
    't'   : ToggleButton,
    'ti'  : ToolItem,
    'tb'  : ToolButton,
    'c'   : CheckButton,
    's'   : SpinButton,
    'ts'  : ToolSpinButton,
    'prg'   : ProgressBar,
    'C'   : ComboBox,
    'Ce'  : ComboBoxEntry,
    'TV'  : GreedyTreeView,
    'TX'  : TextView,
    'daS' : ScrolledDrawingArea,
    'TVS' : ScrolledTreeView,
    'TXS' : ScrolledTextView,
    'cal' : Calendar,
    'sb'  : Statusbar,
    'Col' : ColorSelection,
    'ColB': ColorButton,

    # containers
    'T': Table,
    'W': Window,
    'E': EventBox,
    'X': Expander,
    'V': VBox,
    'H': HBox,
    'le': ComboLE,
    'S' : ScrolledWindow,
    'N' : Notebook,
    'h' : HPaned,
    'v' : VPaned,
    'p' : ViewPort,
    'f' : Frame,
    'Fix' : Fixed,
    'F' : FrameWithLabel,
    'A' : Alignment,
    'Lay' : Layout,
    'LS' : ScrolledLayout,
    


    'B': MenuBar,
    'M': Menu,
    'm': MenuItem,
    'tm': MenuToolButton,
    'O': Toolbar,
    'Z': HandleBox,
    'container_regexp' : '[EXTHVNPSvhpOBmMFfAZ]',
    }


def custom_widget(glade, function_name, widget_name,
                  str1=None, str2=None, int1=None , int2=None):
    cw = MyCustomWidget()
    return getattr(cw, function_name)(str1, str2)



def register(Class, mod, custom=None, force=False):
    """
    register a class to be used within widgets
    'mod' is the string used in layout
    """
    global _W
    exec "global " +  Class.__name__
    exec "%s = Class" % (Class.__name__)
    if mod in _W and not force:
        msg = "Alias %s is already present. Use force=True to force it" % mod
        raise IdentifiedAlreadyPresent(msg)
    _W[mod] = Class        
    
    if custom:
        MyCustomWidget = custom

def register_alias(Class, alias, force=False):
    """
    register an alias for Class
    """
    global _W
    if alias in _W and not force:
        msg = "Alias %s is already present. Use force=True to force it" % alias
        raise IdentifierAlreadyPresent(msg)
    _W[alias] = Class

