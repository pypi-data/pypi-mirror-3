"""
Nick extended configuration
============================

Sqledit configuration may be extended beyond :file:`.sqledit/nicks` file.
You can add configurations for a nick in a subdirectory of :file:`.sqledit`
named as the nick itself. Hooks, layout, or a program can be placed directly
hereq. As an example if you have a nick 'film' defined in
``.sqledit/nicks``::

  [film]
  url = 'postgres://localhost/film

you can add customizations w/o creating a real program. Currently you can
add:

:layout.py: the layout that SqlMask should use when creating the GUI. You can
     create an empty template for this with ``sqledit
     --create-template layout nick``. That's the place where you would
     register your layout.

     This is autoloaded if no ``program.py`` is present
     
:hooks.py: the :ref:`hooks` that will be used as default. You can create an
     empty template for this with ``sqledit --create-template hooks
     nick``. That's the place where you would register yout hooks.
     
     This is autoloaded if no ``program.py`` is present
     
:models.py:  
     this file is for definition of the classes. If you define classes here
     you can set :ref:`relationships` between them so that a mask can display
     parent/child records as director/movies. Many examples in the demo.

     This is autoloaded if no ``program.py`` is present

     You can create an empty template for this with ``sqledit
     --create-template models nick``
     
:program.py: a program that will be executed instead of normal sqledit. There
    is no particular advantage running this instead of creating a real
    standalone program but sometimes it just grows step by step (you start
    with a simple nick, than you add a layout, maybe a hook and you need more
    customization).

    You will call the program as ``sqledit film`` and sqledit will:

    * cd to ~/.sqledit/film
    * execfile('program.py', {'opts' : opts})
    * no other file will be autoloaded in this case

    where ``opts`` is a class that holds the options you set in the nick
    definition (among which ``opts.url``).  You can create an empty template
    for this with ``sqledit --create-template hooks nick``.

    A second reason is that many times a program that uses sqlkit is a
    *very* short script and I found myself spending more time deciding a
    proper name and place, this already makes these decisions for you!

    There is no need to start ``gtk.main()`` since this is no longer the main
    program, sqledit will run it before this moment
"""


import os
from ConfigParser import ConfigParser, NoSectionError

import sqlalchemy

class MissingNickDefinition(Exception): pass
class Opts(object): pass

## Default program.py
TEMPLATE_PROGRAM = """\
import gtk

from sqlkit.widgets import SqlMask
from sqlkit.db import proxy
import models
import hooks

URL = 'postgresql://simone:pr3s33d@ubu64/scuole'
models.Base.metadata.bind = URL
## opts will be added to globals when ececuting this file
db = proxy.DbProxy(bind=opts.URL, metadata=models.Base.metadata)


# no need to run gtk.main()!!!
"""
## Default layout.py
TEMPLATE_LAYOUT = """\
from sqlkit.db import utils

#LAYOUT = """ """

# utils.register_layout('table_name', LAYOUT)
"""

## Default hooks.py
TEMPLATE_HOOKS = """\
from sqlkit.db import utils

class MyHook(object):
    def on_init(self, widget): pass

# utils.register_hook('table_name', MyHook)
"""

TEMPLATE_MODELS = """\
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy.types import *
from sqlalchemy import orm, sql

from sqlkit.db import utils, proxy

Base = declarative_base()

class MyModel(Base):
    __tablename__ = 'demo_model'

# utils.register_class(MyModel)

"""

def read_conf(nick, opts=None):
    """
    read sqledit configurations for 'nick' and return an opts object
    with values in configuration possibly overwritten by values in opts.
    opts can be an optionparse.Values object or a dict.

    :param nick: the nickname for which we want the configuration
    :param opts: the optparse.Values object or a dict
    """
    from copy import deepcopy

    if opts is None:
        opts = Opts()
        
    dbconf = os.path.join(os.path.expanduser('~'), '.sqledit', 'nicks')
    lopts = deepcopy(opts)

    def loop_on_opts(c, opts, nick=nick):
        """
        implements "copy" option in .sqledit/nicks
        """
        for key, val in c.items(nick):
            if key == 'copy':
                loop_on_opts(c, opts, nick=val)
        
        for key, val in c.items(nick):
            if key == 'copy':
                continue
            if getattr(lopts, key, None) is None:
                setattr(opts, key, val)
    
    if os.path.exists(dbconf):
        c = ConfigParser()
        c.read(dbconf)
        loop_on_opts(c, opts, nick)
        read_conf_in_dir(nick, opts)
        if sqlalchemy.__version__ < '0.6':
            if hasattr(opts, 'url5'):
                opts.url = opts.url5

        # option 'mask' in the nicks should not prevail over command line opts!
        # in this case it would prevail due to different key name
        # and parsing order
        if getattr(lopts, 'sqltable', None):
            opts.mask = False

        return opts

    else:
        raise MissingNickDefinition

def get_nick_dir(nick):

    dir_nick = os.path.join(os.path.expanduser('~'), '.sqledit', nick)

    return dir_nick

def read_conf_in_dir(nick, opts):
    """
    Read the conf dir and fill in opts:

    :run: the executable to be... execfile'ed
    :hooks: the file containig the hooks
    """

    nick_dir = os.path.join(os.path.expanduser('~'), '.sqledit', nick)
    opts.run = opts.nick_dir = opts.hooks = opts.models = opts.layout = None
    if os.path.exists(nick_dir):
        opts.nick_dir = nick_dir
        files = os.listdir(nick_dir)

        if 'program.py' in files:
            opts.run = 'program.py'

        if 'hooks.py' in files:
            opts.hooks = 'hooks.py'

        if 'models.py' in files:
            opts.models = 'models.py'

        if 'layout.py' in files:
            opts.layout = 'layout.py'

    
def create_templates(opts):
    """
    Create templates for these
    """
    dir_nick = os.path.join(os.path.expanduser('~'), '.sqledit', opts.nick)
    if not os.path.exists(dir_nick):
        os.mkdir(dir_nick)

    layout = opts.create_templates in ('layout', 'all')
    hooks = opts.create_templates in ('hooks', 'all')
    program = opts.create_templates in ('program', 'all')
    models = opts.create_templates in ('models', 'all')

    if layout:
        filename = os.path.join(dir_nick, 'layout.py')
        if os.path.exists(filename):
            print "File %s already exists, skipping creation" % filename
        open(filename, 'w').write(TEMPLATE_LAYOUT)
    
    if models:
        filename = os.path.join(dir_nick, 'models.py')
        if os.path.exists(filename):
            print "File %s already exists, skipping creation" % filename
        open(filename, 'w').write(TEMPLATE_MODELS)

    if hooks:
        filename = os.path.join(dir_nick, 'hooks.py')
        if os.path.exists(filename):
            print "File %s already exists, skipping creation" % filename
        open(filename, 'w').write(TEMPLATE_HOOKS)
    
    if program:
        filename = os.path.join(dir_nick, 'program.py')
        if os.path.exists(filename):
            print "File %s already exists, skipping creation" % filename
        open(filename, 'w').write(TEMPLATE_PROGRAM)
    
    
    
