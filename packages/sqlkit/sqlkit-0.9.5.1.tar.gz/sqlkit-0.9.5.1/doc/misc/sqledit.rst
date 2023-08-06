.. _sqledit:

==========================================================
 Sqledit - the standalone program to browse and edit data
==========================================================

Sqledit is an application that can be used by anybody without any
programming skill. Basically is just needs a target database that 
can be fed throught a GUI or on the command line.

.. image:: ../img/sqledit.png
   :align: right
   :scale: 40
   :class: preview

.. image:: ../img/sqledit_setup.png
   :align: left
   :scale: 40
   :class: preview


Sqledit is a data editor/browser. At startup it will present a list of all
tables that can be selected for editing (choosing :ref:`mask` or
:ref:`table`) or for introspection.

When run from command line it offers several options:

.. docusage:: ../../sqlkit/scripts/sqledit.py
   :verbatim:

If called without argument it will present a connection dialog:


If sqledit can find a demo in your systems, it will give you the chance to
start it. If you want to type the URL of your db you can directly attempt a
connection or disable it via a checkbox on the right of the entry.

The autoconnect mode is really nice but you may experiment hangs till a
connection timeout if you write a wrong host name.

Since database urls are not nice to write, you can store data in a
configuration file and call nick names instead.

.sqledit
==========

You can write configurations in a file in your home called ``.sqledit/nicks`` and
start sqledit on that configuration using a nickname::

   [invitati]
   URL = postgres://sandro:xxx@my_host/2giugno
   table = partecipazioni_invitato
   dev = True
   field_list = nome, cognome, and all other fields
   order_by = cognome, nome

   [brasile]
   copy = invitati
   field_list = nome, cognome, email, ludo

  
Valid option are URL and any other option for sqledit. The special option
``copy`` force sqledit to read the other definition first and then
overwrite.
In this case 'brasile' shares all options with '2giugno'  but overwrites
field_list.

Even if you don't want to program in Python you may want to add
configuration in a more rich way that allowed in ``.sqledit/nicks``. That
can add for example layout information or information on the relations
between tables so that a Mask can present a ecord and data related to it.

Let's say that that's a gentle introduction to programming with sqlkit...

.. automodule:: sqlkit.misc.conf

schema browser
==============

Introspection of the database will give you the possibility to see all
fields of a table showing all fields, with type, primary keys, foreign keys and
indexes. If you configured a nick to jump directly on a table or any other
configuration allowed by sqledit customization, you'll need the -b
(--browser) option to get to the schema browser.

Options
=======

Calling `sqledit` from a command line under a Linux system with bash
completion you can benefit from the completion that will look for completion
in the .sqledit/nicks file and will suggest some common url (postgresql://,
sqlite://...) 

When primary keys are numeric you probably don't want/need to see them, you
can switch off the visualization with the ``primary key`` toggle button

The ``Load`` toggle button determines if you want to load data when opening a
table. 

``Blank`` toggle button determines if you want to cast blank string fields to
NULL values. When you decide to cast it you may be prompted several times if
you want to save changes that you are not even aware of.


Configuring sqlkit
==================

.. image:: ../img/sqledit_config.png

Sqlkit looks for possible configuration options in some tables, that may or
not be present: _sqlkit_table, and _sqlkit_field.

These tables can be edited directly from the database menu, or via
``<Ctrl-e>`` shortcut.

Completion will help yo configure the fields. Here is the meaning:

table's field
-------------

:name: the table's name 

:search field: this is the **string** field that will be used when searching
   via foreign key. Suppose you are editing a table of movies, and you must
   fill in the director's field. You write some letters and trigger a
   completion, that means you want sqlkit to use that text (e.g. "Fel"), 
   select which directors are present that has that string in... well you
   surely want to search in the last name, but you need to tell sqlkit.

   *search_field* is here for that.

:format: ok, you get back from completion a list of directors you still
   need to show them in a nice way (e.g. first_name, last_name). Here you
   are supposed to used the syntax "%(field_name)s".


attributes'fields
-----------------

:name: the field_name

:description:  the label you want to be used. (Note that when using
   :ref:`related tables <relationships>`  you may indicate
   relation.field_name)

:help_text: this is the tooltip that will be added to the entry

:autostart: you can set an :ref:`autostart` value for the completion

