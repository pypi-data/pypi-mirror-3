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
# FOUNDATION66, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

"""Layout Creation using a GUI description language

This module provides a class named Layout, that uses a description language
to generate xml code for glade to generate Gtk GUI

Each widget is defined by a very concise string similar to e=txt or b=var

"""
import re
import os
import tempfile

import gtk
import gobject

from sqlkit import debug as dbg  
from sqlkit import _
import widgets
from sqlkitplugin import *  # A simple way to import all custom widgets, only used by Builder()

class UnbalancedLayoutCurlyBaces(Exception): pass
class ConnectBeforeShowNotImplemented(Exception): pass

class Layout(object):
    """Generate xml for a specific layout

    Methods:
    xml -- generate the xml for glade
    dim -- returns a tuple w/ the dimentions of the Table that contains the
           layout

    
    A container is generated to contain the widgets. Default is GtkTable (T), but
    other can be choosen by arguments or by specification
    """

    notebook_tabs = []
    _W = widgets._W
    container_regexp = _W['container_regexp']
    shown = False

    def __init__(self,
                 lay,
                 level=0,
                 parent_container="W",
                 opts='T',
                 elements=None,
                 container_id='',
                 addto=None,
                 title=None,
                 geom=(-1,-1),
                 position=None,
                 anchestor=None,
                 label_map=None,
                 ):
        """create a Layout description to be used to generate GUI
        lay: the variable that hold all the information on the layout
        level: nested level used internally by the recursion mechanism
        parent_container: a letter indicating the outermost container
        opts:  options for the outer container. Same syntax as after a '{'
        container_id: ???
        addto: the outermost container will be added to the widget 'addto'
        title: title of the window
        geom: a tuple indicating the desired width and height for the window
        
        """
        #print 'layout init: %s level: %s' % (id(elements), level)

        self.anchestor = anchestor or self
        if label_map:
            self.label_map = map_labels(buf=label_map, private=True)
        else:
            self.label_map = {}
        if elements is None:
            elements = {}

        if level == 0:
            self.connect_dict = {}
            del self.notebook_tabs[0:]

        self.addto = addto
        self.elements = elements
        self.rows = 0           # maximum N. for iteration 
        self.cols = 0           # idem
        self.level = level      # nested level
        self.cells_list = []
        self.cells = {}         # each element is an LWidget or LContainer
        
        self.lay = lay
        self.parent_container = parent_container
        self.container_id = container_id
        self._parse_opts(opts)

        row = 0
        col = -1
        elements_list = self._parse_layout(lay.strip('\n '))
        for el in elements_list:
            ### 'a capo'  both w/ newline *and* @
            if el in ('\n','@'):
                row = row + 1
                self._set_dim(row,col)
                col = -1
            else:
                ## add it to notebook tabs
                if el.startswith('%'):
                    self.notebook_tabs += [re.sub('[%]','',el)]
                    continue
                ### col span
                if el in '-':
                    self._colspan(row,col)
                    col = col + 1
                    continue
                col = col + 1
                ### row span
                if el in '^':
                    self._rowspan()
                    continue
                
                nopts, nested, container_id = self._is_nested(el)
                if nested:
                    new = Layout(nested, self.level + 1,
                                 self.container_flag, opts=nopts,
                                 elements=elements,
                                 container_id=container_id,
                                 anchestor=self.anchestor,
                                 label_map=label_map,
                                 )
                    self.cells[(row,col)] = new.container()
                    new.container().position((row,col))
                else:
                    self.cells[(row,col)] = self._create_lwidget(
                        el, (row, col), container=self.container_flag,
                        elements=elements)
                    #print "Layout(pos) %s: %s,%s" % (el, row, col)
                    #self.cells[(row,col)].position((row, col))

                self.cells_list += [self.cells[(row,col)]]
                #print "Fatta %s,%s %s" % (row, col, self.cells[(row,col)])
#                 for v in dir(self.cells[(row,col)]):
#                     print "%s %s" % (el, v)
                self._set_dim(row,col)   # not always usefull, never harmful

        #print "level: %d opts: %s type %s" % (self.level, opts, type(opts))
        if opts and 's' in opts:
            self._add_status_bar(elements)
        #print "Cells_list: %s" % self.cells_list
        self.lcontainer = self._create_container(row, col, elements)
        self.elements = elements
        #self._add_container_to_elements()
        if self.parent_container == "W" and not addto:
            self._create_window(geom, title,position)
                    
    def container(self):
        return self.lcontainer

    def _create_container(self, row, col,elements):
        # create the containet looking the widget dictionary _W
        #return Table('',self.parent_container, (row,col),'')

        key = self._create_container_id()
        if '|' in self.opts:
            ## well a | is a request to put a line around it, we do that
            ## with a FrameWithlabel 'F' (Frame+Align+Label)
            parent_container = 'A'
        if 'X' in self.opts or '>' in self.opts:
            parent_container = 'X'
        else:
            parent_container = self.parent_container

        cont =  self._W[self.container_flag](key, (row, col),
                                             parent_container,
                                             children_list=self.cells_list,
                                             elements=elements, layout=self.anchestor)

        # in case | I add the Frame and I put now created 'cont' as child
        # Frame F will create 'A' (alignment) and move cont as its child
        if '|' in self.opts:
            key = "F." + self.container_id
            frame = self._W['F'](key, (row, col),
                                 self.parent_container,
                                 children_list=[cont],
                                 elements=elements, layout=self.anchestor)
            cont = frame

        # in case X I add the Expander and I put now created 'cont' as child
        if 'X' in self.opts or '>' in self.opts:
            key = "X." + self.container_id
            expander = self._W['X'](key, (row, col),
                                 self.parent_container,
                                 children_list=[cont],
                                 elements=elements, layout=self.anchestor)
            ## if >> expander will be expanded
            if re.search('>>',self.opts):
                expander.properties['expanded'] = True
                
            cont = expander

        ## notebook labels, if any
        if re.match("N.", key):
            if self.notebook_tabs:
                m = re.search('(.*)_(TOP|LEFT|RIGHT|BOTTOM)$',
                                   self.notebook_tabs[0])
                if m:
                    pos_note = m.group(2)
                    self.notebook_tabs[0] = m.group(1)
                else:
                    pos_note = 'top'
                self.notebook(key, self.notebook_tabs, pos_note.lower())

        return cont

    
    def _create_container_id(self):
        # let's use an element of dict 'elements' as counter, so it is unique
        # for all the nested calls to layout
        if self.container_id:
            container_id = "%s%s" % (self.container_flag,
                                           self.container_id )
        else:
            idx = '%s_progr' % self.container_flag 
            #print "_create_cont_id: %s" % (self.container_flag)
            self.elements.setdefault(idx,-1) 
            self.elements[idx] += 1
            container_id = "%s.%s" % (self.container_flag, self.elements[idx] )

        self.container_id = re.sub("^..",'',container_id)
        return container_id
    def _create_window(self, geom=None, title='Top Window',position=None):
        W = widgets.Window('Window:%s.%s' % (geom[0], geom[1]), (0,0),'W',
                           children_list=[self.lcontainer],
                           elements=self.elements, layout=self.anchestor)       
        self.lcontainer = W
        if title:
            W.properties['title'] = title
        if position in ('NONE',
                        'CENTER',
                        'MOUSE',
                        'CENTER_ALWAYS',
                        'CENTER_ON_PARENT'):
            position = 'GTK_WIN_POS_'+position
            W.properties['window_position']=position
        #print "CREATE_WINDOW: %s" % self.lcontainer
    def _dbg(self, txt):
        if self.dbg == 1:
            print txt
    
    def _create_lwidget(self, el, pos, container,elements):
        ## i extract the type. Default type is 'le'
        #print "Ora creo " + el
        key = re.split("^(?:(.*)=)?(.*)",el)[1] or 'le'
        
        return self._W[key](el, pos, container, elements=elements, layout=self.anchestor)

    def _is_nested(self,el):
        ### is it a final token or a nested layout?
        p = re.compile(r"""
           {                           # start a new nested layout
           (?P<opts>[-=>|a-zA-Z0-9]*)  # it may have some flags HV-=|
           (?P<id>\S*)                 # possible identifier for the container
           (?P<nested>.*)              # the nested layout
           }                           # the end...
        """, re.VERBOSE | re.DOTALL)
        m = p.match(el)
        ### nested: we call Layout again
        if m:
            #print "NESTED: cont_flag: %s opts: %s, nested: %s, id: %s" % \
            #      m.group('cont_flag', 'opts', 'nested', 'id')
            return m.group('opts', 'nested', 'id')
        else:
            #print "NOT NESTED %s" % el
            return None, None, None
    def _colspan(self,row,col):
        ## let's go backword to  search for a defined cell
        for c in range(col,-1,-1):
            if (row,c) in self.cells:
                self.cells[row,c].colspan()
                return
        
    def _rowspan(self,row,col):
        ## let's go backword to  search for a defined cell
        for r in range(row,-1,-1):
            if (r,col) in self.cells:
                self.cells[r,col].rowspan()
                return
        
    def _parse_layout(self, lay):
        lvl = 0
        comment = 0
        where = 'out'
        ret = []
        nested = ''
        i = 0
        for c in lay:
            i += 1
            if c in '#':
                comment = 1
            if c in '\n':
                comment = 0
            if comment == 1:
                continue
            # entering a nested
            if c in '{':
                lvl +=1
            # lowering the nested level
            if c in '}':
                lvl -=1
            if  lvl >= 1:
                nested += c
            if lvl == 0:
                if c in (' ','\t','@','\n'):
                    if len(nested) > 0:
                        ret += [nested]
                        nested = ''
                    if c in ('\n','@'):
                        ret += [c]
                else:
                    nested += c

        if len(nested) > 0:
            ret += [nested]

        if lvl != 0:
            raise UnbalancedLayoutCurlyBaces(lay)
                    
        ## transform any default widget (those w/o modifier '[a-Z]+=') into
        ## L=name e=name. This happens if '-' is in the options
        
        #if True:
        if '-' in self.opts:
            new_ret = []
            for el in ret:
                if re.match('([a-zA-Z0-9]+)=|[%-^\n@{]', el):
                    new_ret += [el]
                else:
                    pattern = re.compile(r"""
                      (?P<val>[^/:]*)         # value
                      (?:/(?P<var>[^:]+))?    # variable
                      (?::(?P<w>[-\d]*))?        # width
                      .?
                      (?P<h>[-\d]+)?           # height
                    """, re.VERBOSE)
                    m = pattern.search(el)
                    if m:
                        new_ret += [ 'L=%s:%s' % (m.group('val') or '',
                                                  m.group('w') or '')]
                        new_ret += [ 'ae=%s:%s' % (m.group('val') or '',
                                                  m.group('h') or '')]
                        
                    else:
                        print "ERRORE: %s scartato" % el
            ret = new_ret
        return ret
    def _dbg_parse_layout(self):
        return  self._parse_layout(self.lay)
    def _dbg_show_objs(self):
        for key,val in self.elements.iteritems():
            print "%-10.10s  ==> %s" % (key, val)
    def _add_status_bar(self, elements):
        self.rows += 1
        sb = self._create_lwidget(
            'sb=StBar', (self.rows,0), self.container_flag, elements)
        self.cells[self.rows,0] = sb
        self.cells_list += [sb]
        self.cells[self.rows,0].pack_properties['right_attach'] = self.cols+1
        #print self.cells[self.rows,0].pack_properties

#     def _parse_flags(self, cont_flag=None):
#         # now is just which container to build, missing "-=|"
#         #container_regexp = '[THVBbNP]'
#         if not  cont_flag:
#             self.container_flag = 'T'    # default container is GtkTable 'T'
#         else:
#             s = re.search('(?P<cont>%s)' % self.container_regexp, cont_flag)
#             if s:
#                 self.container_flag = s.group('cont')
#             else:
#                 raise UnknownContainer    ### FARE!!!!!
            
    def _parse_opts(self, opts=None):
        # now is just which container to build, missing "-=|"
        #container_regexp = '[THVBbNP]'
        # X (gtkExpander) is treated as a modifier rather than a real container
        # X can be added to a normal container flag. If we don't hide it from
        # container_regexp, it would hide the other container
        s = re.search('(?P<cont>%s)' % self.container_regexp.replace('X',''), opts)
        if s:
            self.container_flag = s.group('cont')
        else:
            self.container_flag = 'T'

        #print "_parse_opts: %s" % self.container_flag
        self.opts = opts.replace(self.container_flag,'')
            
    def _set_dim(self,row,col):
        self.rows, self.cols = max(self.rows, row), max(self.cols, col)
        
    def xml(self, filename=None, tmpfile=None, logfile=None):
        """Produces the xml for gtk.Builder() to create the GUI, possibly writes it to file"""

        start = '<?xml version="1.0" encoding="UTF-8" standalone="no"?> <!--*- mode: nxml -*-->'+\
        '\n<interface>\n'

        end = "</interface>\n"

        # not needed if nested layout
        if self.level > 0:
            start = end = ''

        txt = self._clean_items(self.lcontainer.xml())
        if tmpfile:
            tmpfile.write(txt)
        
        #  write it to file?
        if filename:
            f = open(filename,'w')
            f.write("%s\n%s\n%s" % (start, txt, end))
            f.close()
        else:
            return "%s\n%s\n%s" % (start, txt, end)
 
    def create(self, file=None, tmpfile=None):
        """pack the widgets using gtk function (no glade), start from lcontainer"""

        w = self.lcontainer.create(visible=False)
        w.show_all()
        return w
 
    def _clean_items(self, txt):
        pat = re.compile('^(\s+)([^\s<])',re.MULTILINE|re.DOTALL)
        return pat.sub(r'\2', txt)
    
    def  dbg_xml(self):
        return self.lcontainer.dbg_xml()
    
    def dim(self):
        return "DIM %s,%s" % (self.rows+1, self.cols+1)

    def show(self,action=None, x=None):

        if self.shown:
            self.widgets['Window'].show()
        else:
            self.builder = gtk.Builder()

            xml = self.xml()
            try:
                self.builder.add_from_string(xml)
            except: # gtk 2.12 of Builder.ad_from_string() need the length
                self.builder.add_from_string(xml, len(xml))
                
            self.widgets = {}
            for key, val in self.elements.iteritems():
                ## if int, that's just a counter 
                if not isinstance(val, int):
                    self.widgets[key] = self.builder.get_object(key)
            if x:
                if 'Window' in self.widgets:
                    W = self.widgets['Window']
                    if x == 'q':
                        W.connect("delete_event", gtk.main_quit)
                    else:
                        W.connect("delete_event", x)

            if action == 'gtk.main':
                gtk.main()
            ## parent 
            if self.addto:
                container_widget = self.widgets[self.lcontainer.el_def]
                self.addto.add(container_widget)
                
            self.shown = True
            return self.widgets
        
    def gshow(self,action=None, x=None):
        if self.shown:
            self.widgets['Window'].show()
        else:
            self.create()

            self.widgets = {}
            for key, val in self.elements.iteritems():
                ## if int, that's just a counter 
                if not isinstance(val, int):
                    self.widgets[key] = val.gtkWdg

            if x:
                if 'Window' in self.widgets:

                    W = self.widgets['Window']
                    if x == 'q':
                        W.connect("delete_event", gtk.main_quit)
                    else:
                        W.connect("delete_event", x)

            if action == 'gtk.main':
                gtk.main()
            ## parent 
            if self.addto:
                container_widget = self.widgets[self.lcontainer.el_def]
                self.addto.add(container_widget)
                
            self.shown = True
            return self.widgets

    def fshow(self,action=None, x=None, filename=None):
        if not filename:
            tmpdir = tempfile.mkdtemp() 
            filename = os.path.join(tmpdir,'layout.glade')
            print filename
            
        self.xml(file=filename)

        glade = gtk.glade.XML(filename)
        glade.signal_autoconnect(self)
        self.widgets = {}
        for key, val in self.elements.iteritems():
            if not isinstance(val, int):
                self.widgets[key] = glade.get_widget(key)
        if x:
            if 'Window' in self.widgets:
                
                W = self.widgets['Window']
                if x == 'q':
                    W.connect("delete_event", gtk.main_quit)
                else:
                    W.connect("delete_event", x)
        
        if action == 'gtk.main':
            gtk.main()

        ## clean 
        os.unlink(filename)
        os.rmdir(tmpdir)
        return self.widgets
    
    def tip(self, el_def, text):
        if self.shown:
            if isinstance(self.widgets[el_def], gtk.ToolItem):
                self.widgets[el_def].set_tooltip_text(text)
            else:
                self.widgets[el_def].set_tooltip_text(text)
        else:
            self.elements[el_def].properties['tooltip_text'] = text

    def menu(self, el_def, *args):
        """the dictionary must be a list of tuples (key, signal, handler)
        A separator can be as simple as '-' both in key and handler
        
        """

        items = {}
        for d in args:
            d = list(d)
            el_def = el_def.replace('m=','M=')
            menu = self.widgets[el_def]
            #print "menu: ", el_def, menu, self.widgets
            key = d[0]
            if key == '-':
                items[key] = gtk.SeparatorMenuItem()
                #print "Separator"
                d.extend(['activate'])
                d.extend([None])

#             try:
#                 signal = d[2]
#             except IndexError:
#                 signal = 'activate'
                
#             try:
#                 i = d[3]
#             except IndexError:
#                 i = None
                
            if not key in items:
                if key.startswith('gtk-'):
                    items[key] = gtk.ImageMenuItem(key)
                else:
                    items[key] = gtk.MenuItem(key)

                items[key].connect(*d[1:])
            menu.append(items[key])
            menu.show_all()
            
    def connect(self,  *args):
        """the dictionary must be a list of tuples
        (key, signal, handler, arg1, arg2...)"""

        if not self.shown:
            raise ConnectBeforeShowNotImplemented(
                "\n     You must run layout.connect after layout.show()")
            # syntactic check
        if not isinstance(args[0], tuple):
            self.connect_with_id(args)
        else:
            for d in args:
                self.connect_with_id(d)
                
    def connect_with_id(self, args):
        el_def = args[0]
        id = self.widgets[el_def].connect(*args[1:])
        if el_def in self.connect_dict:
            self.connect_dict[el_def] += [(id, args[1], args[2])]
        else:
            self.connect_dict[el_def] = [(id, args[1], args[2])]
        
    def connect_set(self, *args):
        # syntactic check
        if not isinstance(args[0], tuple):
            raise WrongTypeConnect(
                "Layout.connect requires a list of tuples but found: '%s'" % args[0])

        for d in args:
            self.disconnect(d[0], signal=d[1])

        self.connect(*args)
        
    def disconnect(self, el_def, signal=None, id=None, handler=None):
        if id:
            self.widgets[el_def].disconnect(id)
            del self.connect_dict[el_def][id]

        if signal:
            i = 0
            for info in self.connect_dict[el_def]:
                if info[1] == signal:
                    self.widgets[el_def].disconnect(info[0])
                    del self.connect_dict[el_def][i]
                i += 1
            
    def get_connect(self, el_def):
        pass

    def _dbg_widgets(self):
        for key, val in self.widgets.iteritems():
            print "%-15.15s ==> %s" % (key, val)


    def sb(self,txt, seconds=None):
        """
        Push info on Status Bar
        seconds: how many seconds it must stay displayed before being cancelled
        """
        sb = self.widgets['sb=StBar']
        # we need to prevent any attempt to write on a statusbar after the toplevel
        # windows is destroyed. Under Windows you get crashes randomly.
        if not isinstance(sb.get_toplevel(), gtk.Window):
            return
        idx = sb.get_context_id(txt)
        msg_id = sb.push(idx, txt)

        ## delete the message
        def del_text(idx, msg_id):
            if not isinstance(sb.get_toplevel(), gtk.Window):
                return
            try:
                sb.remove_message(idx, msg_id)
            except AttributeError:
                # deprecated in PyGTK 2.2.16
                sb.remove(idx, msg_id)
                    
            return False

        if seconds:
            gobject.timeout_add(seconds * 1000, del_text, idx, msg_id) 

    def notebook(self, el_key, notebook_labels=None, tab_pos='top'):
        """Adds notebook entry for notebooks,

        allows to correct position of tabs, returns a dictionary w/
        label entries"""

        notebook = self.elements[el_key]
        labels_dict = {}
        
        keys = [label.replace(' ','').lower() for label in notebook_labels]
        
        for index, label in enumerate(notebook_labels):
            key = keys[index]
            labels_dict[key] = widgets.NotebookLabel(key, (0, 0),
                                                     'N', self.elements, layout=self.anchestor)
            labels_dict[key].properties['label'] = _(label)
        children = notebook.lw['children_list'] 
        
        new_children = []
        index = 0
        #print children
        for child in children:
            #print "notebook", el_key, index
            #print child.el_def
            key = keys[index]
            new_children += [child , labels_dict[key]]
            index = index + 1

        notebook.lw['children_list'] = new_children

        ## change notebook tab position
        
        # make top the default
        allowed_positions = ["left", "right", "top", "bottom"]
        if tab_pos.lower() not in allowed_positions:
            tab_pos = "top"
            
        tab_pos = "GTK_POS_%s" % tab_pos.upper()
        notebook.properties['tab_pos'] = tab_pos
        
        return labels_dict

    def frame(self, el_key, notebook_labels=[], tab_pos='top'):
        """Adds frame labels

        allows to correct position of tabs, returns a dictionary w/ label entries"""

        ### PIGRIZIA!!! non ho neanche cambiato i nomi delle variabili!
        ### questa funziona va ricongiunta con notebook con un nome unico
        notebook = self.elements[el_key]
        labels_dict = {}
        
        keys = [label.replace(' ','').lower() for label in notebook_labels]
        
        # make top the default ##   PRIMA DIFFERENZA
        allowed_positions = ["left", "right"]
        if tab_pos.lower() not in allowed_positions:
            tab_pos = "top"
            
        tab_pos = "GTK_JUSTIFY_%s" % tab_pos.upper()
        for index, label in enumerate(notebook_labels):
            key = keys[index]
            ### seconda differenza
            labels_dict[key] = widgets.FrameLabel(key,
                                                  (0, 0), 'N', self.elements)
            ### bold face for frame labels
            labels_dict[key].properties['label'] = "&lt;b&gt;%s&lt;/b&gt;" % \
                                                   label
            labels_dict[key].properties['justify'] = tab_pos
            labels_dict[key].properties['use_markup'] = True
        children = notebook.lw['children_list'] 
        
        new_children = []
        index = 0
        for child in children:
            key = keys[index]
            new_children += [child , labels_dict[key]]
            index = index + 1

        notebook.lw['children_list'] = new_children

        ## change notebook tab position
        
        
        return labels_dict

    def prop(self, *args):
        """ this is just a shorter way to set a property"""

        if isinstance (args[0], tuple):
            for prop in args:
                self.prop(*prop)
            return
        else:
            key, name, value = args[0], args[1], args[2]
            
        try:
            ## after self.show(),gtk widgets are there already
            self.widgets[key].set_property(name, value)
        except AttributeError, e:
            self.elements[key].properties[name] = value
            
    def pack(self, *args):
        """ this is just a shorter way to set a pack property"""

        if isinstance (args[0], tuple):
            for prop in args:
                self.pack(*prop)
            return
        else:
            key, name, value = args[0], args[1], args[2]
            
        self.elements[key].pack_properties[name] = value
        
        if 'widgets' in dir(self):
            raise NotImplementedError("pack must be used *before* layout.show()")

    def dialog(self, *args, **kw):
        """
        create a dialog modal that will be destroyed with parent
        """
        
        toplevel = self.widgets.values()[0].get_toplevel()
        return dialog(toplevel, *args, **kw)
    
    def message(self, type=None, text=None, show=True):
        """Pop a message dialog and return the dialog itself

        :param type: info, warn, warning, question, error. Default 'info'.
        :param text: Write this text
        :param show: (boolean), It true (default) shaw_all()
        """
        
        if type is None:
            type = 'info'

        types = {
            'info' : gtk.MESSAGE_INFO,
            'warn' : gtk.MESSAGE_WARNING,
            'warning' :  gtk.MESSAGE_WARNING,
            'question'  : gtk.MESSAGE_QUESTION,
            'error' :     gtk.MESSAGE_ERROR,
            }
        
        window = self.widgets.values()[0].get_toplevel()
        opts = {
            'parent' :  window,
            'flags'  :  gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            'type'   :  types[type],
            'buttons' : gtk.BUTTONS_OK,
            'message_format' : text,
            }
        dialog = gtk.MessageDialog(**opts)
        if show:
            dialog.show_all()
        return dialog

def map_labels(filename=None, buf=None, sep='\t', private=False):
    """
    Return a dictionary with keys the element keys or just the names and
    values a tuple (label, tip)

    If private=False, this will be used in global widget.info
    """

    # if it's a dict, just check that the value is a tuple
    # if not consider it a label and set tip to None
    if isinstance(buf, dict):
        for key, value in buf.iteritems():
            if isinstance(value, basestring):
                buf[key] = (value, None)
        return buf

    if not filename and not buf:
        return {}
    
    info = {}
    if filename:
        f = open(filename)
        buf = f.read()
        f.close()

    for line in buf.strip('\n').split("\n"):
        # tab separated list of name, label, tooltip
        line = line.split(sep)

        name = line[0]
        try:
            label = line[1]
        except:
            label = name

        try:
            tip = line[2]
        except:
            tip = name
        info[name] = (label, tip)

    if private:
        return info
    else:
        widgets.info.update(info)
        
def get_label(name, layout=None):
    """
    return the label associated with 'name'
    if layout is passed, look first if a private layout_map exists

    Slightely different from widget.get_label_and_tip in that we don't
    look for a specific key (eg.: l=name) since we don't have it
    """
    try:
        if layout:
            label, tip = layout.label_map.get(name, None) or widgets.info.get(name, None)
        else:
            label, tip = widgets.info.get(name, None)

        return label or name

    except TypeError, e:
        return name
    
def get_tip(name, layout=None):
    """
    return the help_text associated with 'name'
    if layout is passed, look first if a private layout_map exists
    """
    try:
        if layout:
            label, tip = self.layout.label_map.get(name, None) or widgets.info.get(name, None)
        else:
            label, tip = widgets.info.get(name, None)

        return tip

    except TypeError, e:
        return None
    
def dialog(toplevel = None, layout=None, title='', butts=None, type=None,
           text=None, show=True, mode='', wdict=False):
    """
    A simple way to create a dialog and possibly to setup a layout

    :param toplevel: a toplevel to be bound to (optional)
    :param layout: the layout of the internal widgets
    :param title: a title
    :param butts: a possible tuple of (images/response)
    :param type: the type of dialog: ok, yes-no, yes-no-cancel, ok-cancel,
                 ok-apply-cancel
    :param text: a simple text to be displayed
    :param mode: the mode (defaults to gtk.DIALOG_MODAL if no toplevel,
          gtk.MODAL|gtk.DIALOG_DESTROY_WITH_PARENT, is toplevel is not None)
          use None to prevent settng the mode.
    :param wdict: if True a dict with the reposnse_id as key and the widet as value is added to the
                  reurned values
    returns a (gtk.dialog, Layout object)
    """
    
    if butts is None and type is None:
        type = 'ok'

    if type == 'yes-no':
        butts = (gtk.STOCK_YES, gtk.RESPONSE_YES,
                 gtk.STOCK_NO, gtk.RESPONSE_NO)

    if type == 'yes-no-cancel':
        butts = (gtk.STOCK_YES, gtk.RESPONSE_YES,
                 gtk.STOCK_NO, gtk.RESPONSE_NO,
                 gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)                     

    elif type == 'ok-cancel':
        butts = (gtk.STOCK_OK, gtk.RESPONSE_OK,
                 gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)

    elif type == 'ok-apply-cancel':
        butts = (gtk.STOCK_OK, gtk.RESPONSE_OK,
                 gtk.STOCK_APPLY, gtk.RESPONSE_APPLY,
                 gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)

    elif type == 'ok':
        butts = (gtk.STOCK_OK, gtk.RESPONSE_OK)

    if mode == '':
        if toplevel:
            mode = gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT
        else:
            mode = gtk.DIALOG_MODAL
        
    dialog = gtk.Dialog(title, toplevel, mode, )
    bdict = {}
    if butts:
        for i in range(0, len(butts), 2):
            icon = butts[i]
            response = butts[i+1]
            bdict[response] = dialog.add_button(icon, response)

    lay = Layout(layout, addto=dialog.vbox)

    if text:
        lay.prop(('l=msg', 'label', text))
    lay.show()
    if show:
        dialog.show_all()

    if wdict:
        return (dialog, lay, bdict)
    else:
        return (dialog, lay)
        


