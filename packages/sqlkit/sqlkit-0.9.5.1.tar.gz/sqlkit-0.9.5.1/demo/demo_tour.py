# DISCLAIMER: This is an awful peace of code... I'm aware of it
# but it works and it dosn't hurt anybody it you don't try to read it!...

import os
import re
import tokenize
import keyword

import gtk
import gobject
import pango


from sqlkit.layout import Layout, layout
from sqlkit import debug as dbg

(
   TITLE_COLUMN,
   MODULE_COLUMN,
   DEMO_COLUMN,
   ITALIC_COLUMN,
   MAPPED,
   TOOLTIP,
) = range(6)
CHILDREN_COLUMN = 3

class InputStream(object):
    """ Simple Wrapper for File-like objects. [c]StringIO doesn't provide
        a readline function for use with generate_tokens.
        Using a iterator-like interface doesn't succeed, because the readline
        function isn't used in such a context. (see <python-lib>/tokenize.py)
    """
    def __init__(self, data):
        self.__data = [ '%s\n' % x for x in data.splitlines() ]
        self.__lcount = 0
    def readline(self):
        try:
            line = self.__data[self.__lcount]
            self.__lcount += 1
        except IndexError:
            line = ''
            self.__lcount = 0
        return line



class Demo(object):
    example_pattern = 'ex_.*.py$'
    def __init__(self, pattern=None, xml=True, debug=False, exclude="demo.py"):

        self.pattern = pattern or self.example_pattern
        lay = """
           {V.header  }
           {v 
               {h TVS=a:120.300 {N TXS=txt:250. TVS=tree TVS=el TVS=pack TXS=xml} }
               TXS=note
            } 
        """

        self.l = Layout(lay, opts="s", title="Esempi" , geom=(600,700))

        self.l.notebook('N.0', ['src','tree', 'widget properties','pack properties','xml'])
        self.w = self.l.show(x='q')
        if not xml:
            self.w['N.0'].remove_page(-1)

        tx_src  = self.w['TX=txt']
        tx_note = self.w['TX=note']
        tx_xml = self.w['TX=xml']
        self.src  = tx_src.get_buffer()
        self.xml =  tx_xml.get_buffer()
        self.configure_buffer(self.src)
        self.note = tx_note.get_buffer()

        self.tv_tree = self.w['TV=tree']
        self.create_widget_tree(new=True, toplevel = self.w['Window'])
        self.ts_el   = self.prepare_treeview_elem(self.w['TV=el'])
        self.ts_pack = self.prepare_treeview_tree(self.w['TV=pack'])


        self.demos = self.create_demos(self.pattern, exclude)
        self.tv = self.w['TV=a']
        self.model = self.configure_treeview(self.tv, self.demos, self.src, self.note)
        self.prepare_actions()
        # self.l.menu('m=_File',
        #     ('inspect widgets' , 'activate', self.pop_inspect, ),
        #     ('gtk-quit' , 'activate', gtk.main_quit, ),
        #     )   

    def prepare_actions(self):

        UI = """
          <toolbar name="TbMain">
            <toolitem  action="Execute" />
            <toolitem  action="Quit" />
          </toolbar>
        """

        self.actiongroup = gtk.ActionGroup('Main')
        self.actiongroup.add_actions([
            ('TbMain', None, None),
            ('Execute', 'gtk-execute', 'Debug', None, "Debug via a gtk logger", self.execute_clicked_cb),
            ('Quit', 'gtk-quit', None, "<Control>q", None, gtk.main_quit),
            ])
        self.ui_manager = gtk.UIManager()
        self.ui_manager.add_ui_from_string(UI)
        self.ui_manager.insert_action_group(self.actiongroup, 10)

        self.accel_group = self.ui_manager.get_accel_group()
        self.w['Window'].add_accel_group(self.accel_group)
        header = self.w['V.header']
        toolbar = self.ui_manager.get_widget('/TbMain')
        header.add(toolbar)
        header.show_all()

    def configure_treeview(self, treeview, demos, src, note):
        
        model = gtk.TreeStore(
            gobject.TYPE_STRING,
            gobject.TYPE_STRING,
            gobject.TYPE_PYOBJECT,
            gobject.TYPE_BOOLEAN,
            gobject.TYPE_BOOLEAN,
            gobject.TYPE_STRING,
        )

        treeview.set_model(model)
        selection = treeview.get_selection()
        selection.set_mode(gtk.SELECTION_BROWSE)
        treeview.set_size_request(200, -1)

        sections = []
        for ex in demos:
            if ex.section not in sections:
                sections += [ex.section]
        iters = {}
        for section in sections:
            iter = model.append(None)
            model.set(iter,
                      TITLE_COLUMN, section,
            )
            iters[section] = iter

        for demo in demos:
            iter = model.append(iters[demo.section])
            model.set(iter,
                      TITLE_COLUMN, demo.title,
                      MODULE_COLUMN, demo.filename,
                      DEMO_COLUMN, demo,
                      TOOLTIP, "%s\n\n%s" % (demo.title, demo.doc),
                    )

        cell = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Widget", cell, text=TITLE_COLUMN)
        treeview.append_column(column)
        selection.connect('changed', self.selection_changed_cb)
        treeview.set_tooltip_column(TOOLTIP)
        treeview.expand_all()
        treeview.show_all()
        return model

    def model_foreach_func(self, model, path, iter):

        name = model.get_value(iter, 1)
        if name:
            self.snippet_names += [name]

    def get_names(self):

        self.snippet_names = []
        self.model.foreach(self.model_foreach_func)
        return self.snippet_names
        
    def execute_clicked_cb(self, widget=None):
        """
        toggle visibility of the window that shows debug
        """
        try:
            logger = dbg.get_logger()
            if logger.easytv.w['Window'].get_property('visible'):
                logger.hide()
            else:
                logger.show()
        except:
            pass

    def selection_changed_cb(self, selection):
        model, iter = selection.get_selected()
        if not iter:  # get_selected returns None when you click on the arrow 
            return False
        if model.iter_has_child(iter):
            return True

        if not iter:
            return False

        demo = model.get_value(iter, DEMO_COLUMN)
        self.load_module(demo)
        self.l.sb("file: %s" % demo.filename)

    def load_module(self, demo):
        self.insert_source(demo.body, self.src)
        self.note.set_text(demo.doc)

        ### exec the example
        GLOB = {'Layout': Layout, 'layout': layout, 'gtk': gtk}
        execfile(demo.filename, GLOB)

        self.xml.set_text(GLOB['l'].xml())
        self.last_lo = GLOB['l']
        self.last_w  = GLOB['w']
        self.prepare_treestore_for_elements(GLOB['l'].elements)
        self.create_widget_tree(toplevel=GLOB['w']['Window'])
        GLOB['w']['Window'].set_title(demo.filename)
        self.w['Window'].set_title("Esempio: %s" % (demo.filename))
        return GLOB['l']

    def load_module_by_idx(self, idx):
        """
        Used to open directly an example::

          demo.py 03
          
        """
        for demo in self.demos:
            if demo.idx == idx:
                return self.load_module(demo)
            
    def prepare_treestore_for_elements(self, elements):
        tv = self.w['TV=el']
        ts = self.ts_el
        ts.clear()
        for el, val in elements.iteritems():
            if not isinstance(val, int):
                iter = ts.append(None)
                ts.set(iter, 0, el, 1, val.gtkClass)
                # properties
                for p,v in val.properties.iteritems():
                    child_iter = ts.append(iter)
                    ts.set(child_iter, 2, p, 3, v)

        ts = self.ts_pack
        ts.clear()
        for el, val in elements.iteritems():
            if not isinstance(val, int):
                iter = ts.append(None)
                ts.set(iter, 0, el, 1, val.container_flag, 2, val.gtkClass)
                # PACK properties
                for p,v in val.pack_properties.iteritems():
                    child_iter = ts.append(iter)
                    ts.set(child_iter, 3, p, 4, v)


    def prepare_treeview_elem(self, tv):
        tv.set_rules_hint(True)
        selection = tv.get_selection()
        selection.connect('changed', self.selection_changed_prop_cb)
        ts = gtk.TreeStore(str,str, str, str)
        tv.set_model(ts)

        ## TreeViewColumn & CellRenderer
        heads = ['elem', 'class', 'property', 'value' ]
        for i, v in enumerate(heads):
            tvc = gtk.TreeViewColumn(v, gtk.CellRendererText(), text=i)
            tvc.set_sort_column_id(i)
            tv.append_column(tvc)

        return ts

    def prepare_treeview_tree(self, tv):
        tv.set_rules_hint(True)
        ts = gtk.TreeStore(str, str, str, str, str)
        tv.set_model(ts)

        ## TreeViewColumn & CellRenderer
        heads = ['elem', 'container', 'class', 'property', 'value' ]
        for i, v in enumerate(heads):
            tvc = gtk.TreeViewColumn(v, gtk.CellRendererText(), text=i)
            tvc.set_sort_column_id(i)
            tv.append_column(tvc)


        return ts

    def selection_changed_prop_cb(self, selection):
        model, iter = selection.get_selected()
        if not iter:
            return False

        ## get the class name, position 1
        el_key = model.get_value(iter, 0)
        class_name = model.get_value(iter, 1)
        data = []

        for prop in gobject.list_properties(class_name):
            el = self.last_lo.elements[el_key]
            try:
                val_lay = el.properties[prop.name]
            except KeyError:
                val_lay = None

            try:
                val_gtk = self.last_w[el_key].get_property(prop.name)
            except TypeError:
                val_gtk = None
            data.append((prop.name, prop.nick, prop.value_type, val_gtk, val_lay))
        TreeShow(data)

    def pop_inspect(self, *args):
        dbg.gtk_dbg.show_widgets()

    def create_demos(self, pattern=None, exclude=None):

        file_list = [x for x in os.listdir('.') if re.match(pattern, x) and not re.match(exclude, x)]
        file_list.sort()
        
        demo_list = [Example(ex) for ex in file_list]
        
        return demo_list


    def create_widget_tree(self, new=False, toplevel=None):
        from sqlkit.debug import gtk_dbg
        global show_widgets
        global model
        if new:
            show_widgets = gtk_dbg.show_widgets(lay=False)
            model = show_widgets.create_model(self.tv_tree)

        show_widgets.fill_model(toplevel, model)
        self.tv_tree.expand_all()

    def insert_source(self, data, buf):

        buf.delete(*buf.get_bounds())
        iter = buf.get_iter_at_offset(0)
        #print buf.get_tag_table()
        last_erow, last_ecol = 0, 0
        was_newline = False # multiline statement detection
        for x in tokenize.generate_tokens(InputStream(data).readline):
            # x has 5-tuples
            tok_type, tok_str = x[0], x[1]
            srow, scol = x[2]
            erow, ecol = x[3]

            # The tokenizer 'eats' the whitespaces, so we have to insert this again
            # if needed.
            if srow == last_erow:
                # Same line, spaces between statements
                if scol != last_ecol:
                    buf.insert_with_tags_by_name(iter, ' '*(scol-last_ecol), 'source')
            else:
                # New line.
                # First: Detect multiline statements. There is no special in the tokenizer stream.
                if was_newline is False and last_erow != 0:
                    buf.insert_with_tags_by_name(iter, ' \\\n', 'source')
                # new line check if it starts with col 0
                if scol != 0:
                    buf.insert_with_tags_by_name(iter, ' '*scol, 'source')
            last_erow = erow
            last_ecol = ecol

            if tok_type == tokenize.COMMENT:
                was_newline = True # newline is in tok_str included.
                buf.insert_with_tags_by_name(iter, tok_str, 'source', 'comment')
                continue
            elif tok_type == tokenize.NAME:
                if tok_str in keyword.kwlist:
                    buf.insert_with_tags_by_name(iter, tok_str, 'source', 'keyword')
                    continue
            elif tok_type == tokenize.STRING:
                buf.insert_with_tags_by_name(iter, tok_str, 'source', 'string')
                continue

            # No special format for use. Check for newline.
            was_newline = tok_type in (tokenize.NEWLINE, tokenize.NL)
            buf.insert_with_tags_by_name(iter, tok_str, 'source')

    def configure_buffer(self, buf):
        #print "Configuro %s" % buf
        tag = buf.create_tag('title')
        tag.set_property('font', 'Sans 18')

        tag = buf.create_tag('source')
        tag.set_property('font', 'monospace')
        tag.set_property('pixels_above_lines', 0)
        tag.set_property('pixels_below_lines', 0)
        tag = buf.create_tag('keyword', foreground='#00007F',
                                weight=pango.WEIGHT_BOLD)
        tag = buf.create_tag('string', foreground='#007F00')
        tag = buf.create_tag('comment', foreground='#7F007F',
                                       style=pango.STYLE_ITALIC)


    def iconify(self):
        self.w['Window'].iconify()
        
class TreeShow(object):
    def __init__(self, data):
        l = layout.Layout( "TVS=a", opts="Vs")
        w = l.show()
        tv = w['TV=a']

        ts = gtk.ListStore(str, str, str, str, str)
        tvc = gtk.TreeViewColumn('prop', gtk.CellRendererText(),text=0)
        tvc.set_sort_column_id(0)
        tv.append_column(tvc)
        
        cell = gtk.CellRendererText()
        #cell.set_property('style', pango.STYLE_BOLD)
        tvc = gtk.TreeViewColumn('lay val', cell, text=4)
        tvc.set_sort_column_id(4)
        tv.append_column(tvc)

        cell = gtk.CellRendererText()
        cell.set_property('style', pango.STYLE_ITALIC)
        tvc = gtk.TreeViewColumn('gtk val', cell, text=3)
        tvc.set_sort_column_id(3)
        tv.append_column(tvc)

        cell = gtk.CellRendererText()
        cell.set_property('style', pango.STYLE_ITALIC)
        tvc = gtk.TreeViewColumn('nick', cell, text=1)
        tvc.set_sort_column_id(1)
        tv.append_column(tvc)


        tv.set_model(ts)
        for i in data:
            iter = ts.append(None)
            ts.set(iter, 0, i[0], 1, i[1],  2, i[2],
                   3, i[3],  4, i[4])


class Example(object):

    def __init__(self, filename):

        self.doc, self.body = self.readexample(filename)
        self.filename = filename
        self.description = self.doc.splitlines()[0]
        self.doc = "\n".join(self.doc.splitlines()[1:])
        # ex_01b_import_table.py
        m = re.match('(ex_)?(?P<idx>.*?)_(?P<name>.*).py', self.filename)
        self.idx = m.group('idx')
        self.name = m.group('name')
        self.section, self.title = self.description.split('/')
        
    def readexample(self, file_name):
        """
        read the __doc__ of the example and separate it from the body
        """

        idf = file(file_name,'r')
        txt = idf.read()
        idf.close()
        pat = re.compile(r'''
        ^"""(?:(?P<doc>.*?)""")\s*(?P<body>(.*))
        ''', re.MULTILINE| re.DOTALL|re.VERBOSE)
        m = pat.search(txt)
        if m:
            return  m.group('doc','body')
        else:
            return (None, None)

    def __str__(self):
        return self.filename
    
    def __repr__(self):
        return "<Example: %s>" % self.filename
