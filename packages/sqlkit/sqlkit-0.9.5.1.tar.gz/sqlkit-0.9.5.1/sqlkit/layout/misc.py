import os
import sys

import gtk

from sqlkit import _

### utility: stock icons    
SK_ICONS = (
    ('cal15.png', 'sk-calendar'),
    ('keys.png', 'sk-pkeys'),
    ('table-load.png', 'sk-table-load'),
    )


def add_stock_icons(*icon_list):

    factory = gtk.IconFactory()

    for icon_file, stock_id in icon_list:

        if os.path.exists(icon_file):
            filename = icon_file
        else:
            filename = os.path.join(os.path.dirname(__file__), icon_file)
            if not os.path.exists(filename):
                filename = os.path.join(os.path.dirname(sys.executable), icon_file)

        pixbuf = gtk.gdk.pixbuf_new_from_file(filename)
        iconset = gtk.IconSet(pixbuf)
        factory.add(stock_id, iconset)
        factory.add_default()

add_stock_icons(*SK_ICONS)

class StockMenuItem(gtk.ImageMenuItem):
    
    def __init__(self, label, stock, size=gtk.ICON_SIZE_MENU):
        gtk.ImageMenuItem.__init__(self, label)
        image = gtk.Image()        
        image.set_from_stock(stock, size)
        self.set_image(image)
        self.show_all()

class EasyTreeView(object):
    def __init__(self, cols, tv=None, model=None, sort=True,
                 resize=True, show=True, but='', title='EasyTreeView'):
        if tv:
            self.tv = tv
        else:
            self.l = self._get_layout(but, title=title)
            self.l.prop('Window', 'visible', show)
            self.w = self.l.show()
            self.tv = self.w['TV=a']
            
            self.l.connect(
                ('tb=gtk-quit', 'clicked', lambda l: self.w['Window'].destroy()),
                )

        self.columns = []
        self.column_names = []
        for col in cols:
            if isinstance(col, str):
                self.column_names += [col]
                self.columns += [str]
            if isinstance(col, tuple):
                # the second position is for type
                self.column_names += [col[0]]
                self.columns += [col[1]]

        if not model:
            self.model = gtk.TreeStore(*self.columns)
        else:
            self.model = model

        self.tv.set_enable_search(True)
        self.tv.set_model(self.model)
        self.tvc = {}
        for i, col in enumerate(self.column_names):
            cell = gtk.CellRendererText
            if self.columns[i] == bool:
                cell = gtk.CellRendererToggle
                self.tvc[col] = gtk.TreeViewColumn(_(col), cell(), active=i)
            else:
                self.tvc[col] = gtk.TreeViewColumn(_(col), cell(), text=i)
            if sort == True:
                self.tvc[col].set_sort_column_id(i)
            self.tvc[col].set_resizable(resize)
            self.tv.append_column(self.tvc[col])

    def show(self):
        self.w['Window'].show_all()

    def hide(self):
        self.w['Window'].hide()

    def _get_layout(self, but, title=None):
        from sqlkit import layout
        lay = """
          {O tb=gtk-quit  tb=gtk-clear %s}
          TVS=a
        """ % (but)
        #dbg.write()
        return layout.Layout(lay, opts="s", title=title)


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

