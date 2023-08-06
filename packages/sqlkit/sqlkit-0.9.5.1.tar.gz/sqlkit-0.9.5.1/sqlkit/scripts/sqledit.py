#!/usr/bin/python
# Copyright (C) 2005-2006-2007-2008-2009-2010, Sandro Dentella <sandro@e-den.it>
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
usage: %prog [options] [[url|nick] table]
   -u, --url = URL: an url to open (eg postgres://user:pass@host/dbname)
   -n, --nick = nick: a nick in ~/.sqledit/nicks
   -t, --table = table: open table 'table'
   -m, --mask: open a SqlMask (default is SqlTable)
   -b, --browser: open the table browser reguardless of nick configuration
   -T, --sqltable: open a SqlTable (default when -t is used)
   -d, --dev: open in 'dev' mode
   -D, --debug: print debug
   -g, --gtk-debug: use LogTheMethods
   -S, --sql=statement: execute statement (requires -t)
   -a, --all-tables: read all table on startup (very slow)
   -f, --field_list=fields: comma (or space) separated field list 
   -o, --order_by=fields: comma separated field list
   -c, --configure: open SqlMasq on _sqlkit_table or create it
   -v, --version: prin version and exit
   -L, --load: load data when opening a table (if no table is directly
         opened, set LoadData)
   -l, --limit=LIMIT: limit to LIMIT rows
   -i, --ipython: if ipython is present it opne an ipython shell
   -C, --create-templates=mode: create in one of these modes: layout,
         hooks, programm, models, all
   , --create-tables: Create all tables in models define in metadata (models.metadata or Base.metadata)
"""

import sys
import os
import re
import datetime
import user
import locale

import pygtk
pygtk.require("2.0")
import gtk

if not 'LANG' in os.environ:
    my_locale, my_code = locale.getdefaultlocale()
    LANG = "%s.%s" % (my_locale, my_code)
    os.environ['LANG'] = LANG
    import locale
    locale.setlocale(locale.LC_ALL, '')

import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from sqlalchemy.engine import url

import sqlkit
from sqlkit import fields, DbProxy, _
from sqlkit.misc import conf, optionparse

RESPONSE_DEMO = 1
DEMO_DIRS = [
    os.path.join('demo', 'sql'),
    os.path.join( os.path.dirname(os.getcwd()), 'demo', 'sql'),
    '/usr/share/doc/python-sqlkit/demo/sql',
    ]
try:
    ## this is needed so that this file can be 'execfile-ed' in the 'docusage'
    ## directive of the documentation. In that context __file__ is not defined
    DEMO_DIRS += [
        os.path.join( os.path.dirname(__file__), 'demo', 'sql'),
        os.path.join( os.path.dirname(os.path.dirname(__file__)), 'demo', 'sql'),
        os.path.join( os.path.dirname(sqlkit.__file__), 'demo', 'sql'),
        os.path.join( os.path.dirname(os.path.dirname(sqlkit.__file__)), 'demo', 'sql'),
        ]
except:
    pass

class ConnectionDialog(object):
    TITLE = _('Connection setup') + "(sqlkit %s)" % sqlkit.__version__
    URL_DB_BACKEND='http://www.sqlalchemy.org/docs/dialects/index.html'
    URL_SQLKIT='http://sqlkit.argolinux.org/misc/sqledit.html'
    GENERAL_MSG = _("""
    You can indicate the database you want to connect to
    using an URI in the form of:
    <b>postgres://localhost/dbname</b>
    <b>sqlite:///dbname</b>
    or using password and username:
    <b>mysql://sandro:pass@host/dbname</b>
    """)

    def __init__(self):
        """
        represent the errors in self.validation_errors and raise ValidationError
        to correctly propagate the error upwards
        """

        lay = """
            l=general:<
            { lb=backend_help lb=sqledit } 
            { e=url:30 c=auto}
            l=errors:<
        """
        from sqlkit.layout import layout
        self.wdict = {}
        self.dialog, self.l = layout.dialog(mode=0,
            layout=lay, type=False, butts=None, title=self.TITLE)

        BUTTS = (
            (_('Run Demo'), RESPONSE_DEMO),
            (gtk.STOCK_OK, gtk.RESPONSE_OK),
            (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL),
            )

        for icon, response in BUTTS:
            self.wdict[response] = self.dialog.add_button(icon, response)

        self.wdict[gtk.RESPONSE_OK].props.sensitive = False
        self.wdict[RESPONSE_DEMO].props.sensitive = False
        
        self.dialog.set_default_response(gtk.RESPONSE_OK)

        self.l.widgets['l=general'].set_markup(self.GENERAL_MSG)
        self.l.widgets['l=general'].props.selectable = True
        self.l.widgets['l=general'].props.xpad = 10
        self.l.widgets['l=general'].props.ypad = 10
        self.l.widgets['l=errors'].props.selectable = True
        #l.widgets['a=url'].set
        self.dialog.show_all()
        self.l.widgets['e=url'].grab_focus()
        self.l.widgets['lb=backend_help'].set_uri(self.URL_DB_BACKEND)
#        self.l.widgets['lb=backend_help'].props.label = _('backend help')
        info = _('Info on available backend:\npostgres, mysql...')
        info2 = _('Sqledit manual page')
        self.l.widgets['lb=backend_help'].set_tooltip_text(info)
        self.l.widgets['lb=sqledit'].set_tooltip_text(info2)
        self.l.widgets['lb=sqledit'].set_uri(self.URL_SQLKIT)
        self.l.widgets['l=errors'].props.wrap = True
        info_auto_try = _("""Try continuosly to connect.
        Nice and usefull but may cause temporary blocks
        if you enter an inexistent hostname
        """)
        self.l.widgets['c=auto'].set_tooltip_text(info_auto_try)
        self.l.widgets['c=auto'].set_active(True)
        self.l.connect(
            ('lb=backend_help', 'clicked', self.clicked_cb),
            ('lb=sqledit', 'clicked', self.clicked_cb),
            )
        self.l.widgets['e=url'].connect('changed', self.changed_cb)
        self.l.widgets['e=url'].connect('activate', self.activate_cb)
        self.set_error_msg('')
        self.add_demo()
        tip = _('If you enter a wrong hostname\nthe application may hang some seconds ' + \
                'till the natural network timeout. \nUncheck the flag on the right to disable this feature')
        self.l.widgets['e=url'].set_tooltip_text(tip)

    def changed_cb(self, entry):
        
        global opts
        url_text = entry.get_text()
        try:
            URL = url.make_url(url_text)
        except Exception, e:
            self.wdict[gtk.RESPONSE_OK].props.sensitive = False
            return
        self.set_error_msg("" )
        if URL.drivername and URL.database and (URL.host or (
            URL.drivername == 'sqlite' and os.path.exists(URL.database))):
            opts.url = url_text
            ## a checkbox determines if we try continuosly
            auto = self.l.widgets['c=auto'].get_active()
            if auto:
                self.activate_cb(entry)
        else:
            self.wdict[gtk.RESPONSE_OK].props.sensitive = False
            opts.url = None
        
    def activate_cb(self, entry):
        url_text = entry.get_text()
        self.set_error_msg(_("Attempting to connect to %s") % url_text)
        try:
            open_db(exc=True)
            self.set_error_msg(_("Connected to %s") % url_text, 'sea green')
            self.wdict[gtk.RESPONSE_OK].props.sensitive = True
        except Exception, e:
            self.set_error_msg(str(e), 'red')
            self.wdict[gtk.RESPONSE_OK].props.sensitive = False

        return 
        
    def clicked_cb(self, widget):
        import webbrowser
        webbrowser.open(widget.get_uri())
        
    def run(self):
        global opts
        response = self.dialog.run()
        if response == gtk.RESPONSE_CANCEL:
            sys.exit()
        elif response == RESPONSE_DEMO:
            start_demo()
            self.dialog.destroy()
            return response
        else:
            opts.url = self.l.widgets['e=url'].get_text()
            if open_db():
                self.dialog.destroy()
            else:
                pass
        return response

    def add_demo(self):

        demo_message = _('A complete demo of all the features of the sqlkit package')
        demo_missing = _('The demo was not found, if you know where it is,\n' + \
                         'run it manually: python demo.py')
        if find_demo():
            self.wdict[RESPONSE_DEMO].props.sensitive = True
            self.wdict[RESPONSE_DEMO].set_tooltip_text(demo_message)
        else:
            self.wdict[RESPONSE_DEMO].set_tooltip_text(demo_missing)
            

    def set_error_msg(self, text, color='black'):
        from gobject import markup_escape_text

        markup = '<span foreground="%s">%s</span>' % (color, markup_escape_text(text))
        self.l.widgets['l=errors'].set_markup(markup)
        

def find_demo():
    """
    find the demo dir looking in fixed positions or in module sqlkit.demo
    """
    
    found_demo = None
    for demo_dir in DEMO_DIRS:
        demo_program = os.path.join(demo_dir, 'demo.py')
        if os.path.exists(demo_program):
            found_demo = demo_dir
    try:
        from sqlkit.demo import sql
        demo_dir = os.path.dirname(sql.__file__)
        found_demo = demo_dir

    except ImportError, e:
        pass
    return found_demo

def start_demo():
    """
    Start the demo application
    """

    demo_dir = find_demo()
    demo_program = os.path.join(demo_dir, 'demo.py')
    if os.path.exists(demo_program):
        os.chdir(demo_dir)
        sys.path.insert(0, os.getcwd())
        execfile('demo.py', {})

def open_db(exc=False):
    global db, models

    db = None

    if getattr(opts,'nick_dir', None):
        os.chdir(opts.nick_dir)
        sys.path.append(opts.nick_dir)
        if opts.run and not opts.browser:
            os.getcwd()
            execfile(opts.run, {'opts': opts})
            sys.exit()
        else:
            if opts.models:
                import models
                try:
                    if opts.create_tables:
                        if not models.Base.metadata.bind:
                            models.Base.metadata.bind = opts.url
                        models.Base.metadata.create_all()
                except Exception, e:
                    print e
                    pass
                try:
                    db = models.db
                except AttributeError:
                    pass

            if opts.hooks:
                import hooks
            if opts.layout:
                import layout
            
    try:
        db = DbProxy(bind=opts.url)
        db.metadata.bind.connect()
        return True
    except Exception, e:
        raise e
        if exc:
            raise e
        else:
            if e.message == 'No module named MySQLdb':
                print "You need to install mysql driver (python-mysqldb under debian)"
            sys.exit(1)
        return False

def program():

    # Don't move this import before parsing opt gtk_debug, it won't work!
    from sqlkit.misc import table_browser
    
    global opts, tb

    if args:
        if re.search('://', args[0]):
            opts.url = args[0]
        else:
            opts.nick = args[0]

    if len(args) >1:
        opts.table = args[1]

    if opts.create_templates:
        conf.create_templates(opts)
        sys.exit(0)

    if opts.debug:
        dbg.debug(True)

    if opts.nick:
        try:
            opts = conf.read_conf(opts.nick, opts)
        except conf.NoSectionError:
            print "No nick named '%s'" % opts.nick
            sys.exit(1)

    if not args and not opts:
        dialog = ConnectionDialog()
        dialog.set_error_msg(os.environ['LANG'])
        response = dialog.run()
    else:
        response = None
        open_db()

    fields.BLANK_OK = True
    if not response == RESPONSE_DEMO:
        session = db.get_session()

        try:
             if opts.table and not opts.browser:
                 tables = re.split('[ ,]+', opts.table)
                 for t in tables:
                     if len(tables) > 1:
                         single = False
                     else:
                         single = True
                     tb = table_browser.open_sqlwidget(t, single, opts, db)
             elif opts.configure:
                 tb = table_browser.sqlkit_model(dbproxy=db, single=True)

             else:
                 title = session.bind.url.database
                 tb = table_browser.TableBrowser(db, title=title, opts=opts, x='quit')    

        except OperationalError, e:
            if opts.debug:
                raise e
            else:
                print e.orig
                sys.exit(1)

    

###### Program
def main():
    global opts, args

    opts, args = optionparse.parse(__doc__)

    if opts.version:
        print sqlkit.__version__
        sys.exit(0)

    if opts.gtk_debug:
        from sqlkit import debug as dbg
        dbg.trace_class(ok='SqlTable|SqlWidget|SqlMask|Completion')
        but = 'set_fkey_descr|(lookup|set|get)_value|[el]ne_cb|match_func' + \
           '|cell_default_cb|cell_bool_cb|_lookup_value|is_fkey'
        dbg.trace_function(exclude=but)
        dbg.debug(True, gtk=True)
        import sqlkit
        
    program()

    if opts.ipython:
        try:
            gtk.set_interactive(True)
        except AttributeError:
            print "This version of gtk does'n not have 'set_interactive', sorry."
            sys.exit(1)
        try:
            import IPython
            from IPython.Shell import IPShellEmbed
            ipshell = IPShellEmbed([])
            ipshell()
        except ImportError, e:
            print "Interactive demo needs ipython. Quitting."
    else:
        try:
            gtk.main()
        except KeyboardInterrupt:
            pass

if __name__ == '__main__':

    main()
