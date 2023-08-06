#!/usr/bin/env python
# -*- coding: utf-8 -*-   -*- mode: python -*-

"""
opens the demo console or directly an example defined by its number:

./demo.py 25
./demo.py -N 40b

usage: %prog [opts] ex_number
   -N, --no-gtk-debug: gtk debug
   -g, --gtk: gtk debug in window
   -i, --interactive: set interactive so that ipython can interact
   -t, --test: run all snippets and run t.reload() for each of them
   -o, --offset=n: skip the first 'n' snippets
   -n, --number=l: stop after 'n' snippets
   -r, --reload: reload all snippets (some will stop for confirmation)
   -e, --exit: exit on exception
   -x, --existent-db: don't delete the demo db if it exists
"""

from __future__ import with_statement
import sys
import os
import sqlite3
import weakref
from contextlib import closing

pdir = os.path.dirname(os.getcwd())
ppdir = os.path.dirname(pdir)
sys.path.insert(0,pdir)    
sys.path.insert(0,ppdir)    

import sqlkit
from sqlkit.misc import optionparse
opts, args = optionparse.parse(__doc__)

import gtk

if opts.gtk:
    from sqlkit import debug as dbg
    dbg.debug(True)
    dbg.debug(True, gtk=True)
    dbg.trace_class(ok='SqlTable|SqlWidget|SqlMask|Completion')
    but = 'set_fkey_descr|(lookup|get)_value' + \
        '|lookup_value|is_fkey'
    dbg.trace_function(exclude=but)

from demo_tour import Demo
from sqlkit.widgets import SqlMask, SqlTable
from sqlkit.db import proxy, defaults, utils
import model

class MissingExampleError(Exception): pass

def init_db():

    with closing(sqlite3.connect(model.DB_FILE)) as db:
        with open('model/schema.sql', 'r') as schema:
            db.cursor().executescript(schema.read())
        db.commit()

class DemoSql(Demo):
    def load_module(self, demo):
        ### fill text: src, notes, and xml
        self.insert_source(demo.body, self.src)
        self.note.set_text(demo.doc)

        ### exec the example
        GLOB = {
            'sqlkit': sqlkit,
            'SqlMask': SqlMask,
            'SqlTable': SqlTable,
            'gtk': gtk,
            'db': model.db,
            'model': model,

            }
        execfile(demo.filename, GLOB)
        self.last_lo = GLOB['t'].lay_obj
        self.last_w  = GLOB['t'].widgets
        self._t = weakref.ref(GLOB['t'])
        try:
            self.t1 = GLOB['t1']
        except:
            pass
            

        #self.xml.set_text(GLOB['l'].xml())
        self.create_widget_tree(toplevel=GLOB['t'].widgets['Window'])
        self.prepare_treestore_for_elements(GLOB['t'].lay_obj.elements)
        GLOB['t'].widgets['Window'].set_title(demo.filename)
        self.w['Window'].set_title("Example: %s" % (demo.filename))

        while gtk.events_pending():
            gtk.main_iteration()

        return GLOB['t']

    @property
    def t(self):
        try:
            return self._t()
        except AttributeError:
            raise MissingExampleError("The example was not found")
    
    
if not opts.existent_db and os.path.exists(model.DB_FILE):
    try:
        os.remove(model.DB_FILE)
    except OSError:
        print "No way to remove file", model.DB_FILE
        # No write permission - no problem, a temporary db will be created
        pass
if not os.path.exists(model.DB_FILE):
    init_db()
    
d = DemoSql(xml=False, debug=True)
d.tv.collapse_all()
if not os.access('images', os.W_OK):
    print "WARNING: \n  Missing write permission on 'images' directory"
    print "  Image upload is not possible\n"

if args:
    d.iconify()
    d.load_module_by_idx(args[0])
    def quit(widget):
        gtk.main_quit()

    try:
        hid = d.t.connect('delete-event', quit)
        d.t._ids['delete_event'] = (d.t, hid)
    except MissingExampleError:
        print "No such example ", args[0]
        sys.exit(1)
    except AttributeError, e:
        pass

if opts.test:
    start = opts.offset and int(opts.offset) or 0
    stop = opts.number and start + int(opts.number) or None
    print start, ':', stop
    for demo in d.demos[start:stop]:
        print "------------------ %s %s --------------" % (d.demos.index(demo), demo)
        try:
            t = d.load_module(demo)
            if opts.reload:
                t.reload()
        except Exception, e:
            print e
            if opts.exit:
                sys.exit(1)

if opts.gtk:
    d.execute_clicked_cb

        
if __name__ == '__main__':
    if opts.interactive:
        try:
            gtk.set_interactive(True)
        except AttributeError:
            print "This version of gtk doesn't have 'set_interactive', sorry."
            sys.exit(1)
        try:
            import IPython
            from IPython.Shell import IPShellEmbed
            ipshell = IPShellEmbed([])
            print "The last opened table is hold in variable 'd.t' (i.e.: demo.table)"
            ipshell()
        except ImportError, e:
            print "Interactive demo needs ipython. Quitting."
    else:
        print "Try option -i to try sqlkit interactively"
        gtk.main()
    
