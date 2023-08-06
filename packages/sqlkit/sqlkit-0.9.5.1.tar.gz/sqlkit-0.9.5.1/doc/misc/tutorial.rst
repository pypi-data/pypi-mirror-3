.. _tutorial:

==================
 Sqledit Tutorial
==================

Intended audience
===================

This is meant as a tutorial for the :command:`sqledit` command that is part of
sqlkit. It's intended audience is anybody who is interested in editing data
in a database (as opposed to editing the *structure* of the database).

No programming skill is required, but if you are supposed to install it
yourself, you may need to understand at least a little bit of your operating
system (but that may be as simple as a double click if you use bundles).

Installation
============

According to you operating system and setup you may find the very easy way
for you. You may not event need to know which are the dependancies that are
explained below for the curious ones.

.. _ubuntu-install:

Installing under Debian/Ubuntu
-------------------------------

On Ubuntu lucid (10.04) and probably also others >= 9.10
you can prepare dependencies::

  sudo add-apt-repository ppa:toobaz/sqlkit
 
On Debian::

  echo deb http://ppa.launchpad.net/toobaz/sqlkit/ubuntu lucid main | sudo tee /etc/apt/sources.list.d/sqlkit.list
  sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 39012CF8

and install it as follows (this installs python drivers for PostgreSQL and
Mysql as well)::

  sudo apt-get update
  sudo apt-get install python-sqlkit python-psycopg2 python-mysqldb

I'll try to keep this updated as the official package

.. _windows-install:

Installing under Windows
------------------------

The easiest way is to use `Windows Package Manager`_  that handles 
dependencies (that can turn usefull for other software too). The
installation process becomes as easy as:

  * download and install `Windows Package Manager`_
  * start it, select sqlkit and install (you may want to select/inistall
    also the database drivers for PostgreSql and MySQL)

If you want to go the "hard" way you can install all peaces separately but
still use the Pygtk all-in-one installer (thanks to Dieter Verfaillie):

  * download and install Python_
  * download and install Pygtk-all-in-one_
  * download sqlkit-VER.zip_ unzip and install by doing::
    
      python setup.py install

    Note that python may not be in the PATH so you may need to write it
    explicetly.
  
Installig under MacOS
---------------------

You can install and run Sqlkit under MacOS also. You can use the all-in-one
boundle_ (thanks to Anders F. Björklund) or install from MacPorts. 

Dependencies
------------

Sqlkit depends on the following packages:

:Python: sqledit it's a Python script. It should work with python 2.4 and
         following. But if you used 2.4 be sure to add the driver for sqlite
         that was added to the main distribution only starting from 2.5.

:PyGTK:  any Linux desktop distribution has it already installed, in case
         it does not have it, it should be trivial to do. In Debian-derived
         systems (e.g.: Ubuntu), you simply run::

 	     apt-get install python-gtk2

         In a Windows system it used to be a difficult task but now it's
         very simple. Please follow the instructions on the `pygtk site`_

:sqlalchemy: this is the core of the sql staff. It's a layer that builds SQL
         statements and invokes the backend drivers. It takes care of
         inspecting the database and so on. You need at least release 0.5 but
         0.5.4 would be much better.

:python-dateutil: needed for computation on dates, used in filters (e.g: date
         >= 'm-1', means date >= starting of last month), see :ref:`date_filters`.


:babel:   needed for localization of numbers and dates
          
:setuptools: needed for the installation and to check version of sqlalchemy

:drivers: don't forget to add the driver for the backend of your choice, the
          only driver included is for ``sqlite``, that is the database of
          the demo and is included in the python distribution since python
          2.5. 
	  

If you have setuptools installed in your system, you can install whatever
you need simply with::

   easy_install sqlkit

and probably you'd have better results using ``pip``::

   easy_install pip
   pip install sqlkit

remember to install the backend driver, these are the examples for postgresql
and mysql::

   pip install psycopg2
   pip install MySQL-python


sqledit/sqlkit
==============

.. image:: ../img/sqledit.png
   :align: right

Now you should have a working setup. The command we are going to familiarize
with is ``sqledit`` that is based on a library named ``sqlkit``. If you are
a programmer and are interested in the sqlkit package you can find extensive
documentation in the `web site`_

Programming with sqlkit is a pretty simple experience that allows you to use
many more features than available with ``sqledit``, nevertheless you can do
a lot of simple tasks by using ``sqledit`` alone.

.. versionadded:: 9.1

Sqledit has a flexible :ref:`configuration system <sqledit>` that allows you
to add many code snippets w/o writing a true program, so that even if you
decide to start with sqledit due to it's simplicity you can add more
configurations as far as you needs them. I personally started using that as
my preferred way.

Sqledit can be used:

* from command line, possibly adding arguments and options
* from a menu entry interactively writing the URL of the database you want to edit.

If you start it with no arguments you are presented a dialog with an entry
and 3 buttons:

* you can write the url of a database of yours in the entry, e.g.::

    postgres://localhost/dbname     # sqlalchemy 5
    postgresql://localhost/dbname   # sqlalchemy 6+
    sqlite:///db.sqlite
    mysql://name:pass@host/dbname
  
  .. note::
     the URL for a sqlite database has 3 '/'if the database is in your
     current directory, 4 if you need to pass a file starting with '/'.

* start the demo tour

Sqledit table listing
=====================


The demo tour is meant for developers, so that it shows source code as well,
but it's also suitable for our introduction and is a living database, so we
will use that in this tutorial.

The demo presents you some examples on the left. Let's start with...  the
last one! We start with the last one because it's the window you will
see when you start sqledit with an address of a real database (the demo one
in this case).



The table listing
-----------------

The table listing of the database is shown above: clicking on a table
name pops a menu that lets you choose between:

* table view: representation of the table in a spreadsheet fashion
* mask view:  a form with each field is displayed
* table reflection: sqledit reads the definition for that table

Tables
=======

Let's choose a table view: 

.. image:: ../img/table.png

each field of the table is represented in a column, each type has different
representations:

:text: a simple cell will render the text

:numbers: each number is adjusted to the right

:dates: dates are represented in you preferred locale that is argued from
    LANG variable or from locale module information

:boolean: a checkbox is used. It the NULL value is accepted, clicking the
    checkbox will loop between True, False and undefined

:intervals: intervals are really poorly rendered at the moment...

:foreign keys: foreign keys are represented via the value they point to in
    the remote table. At present only simple (not compound keys) are
    allowed. To help you detect that that's a ForeignKey it's drawn in blue.
    Just to be pedantic: you won't see the real value (that may happen to be
    an id, normally not very interesting), you will rather see the value it
    points to... 

    As you can realize there is not real *value* where is points. An id
    points to a record of a table (e.g.: director id 1 may point to the record
    in director table where ``last_name`` is *Fellini*), but *Fellini* is not
    the value of the id: it's rather a representation of the record that in
    many circumstances may be enough (and in many other is not).

    So I introduced a rule: I represent it with the value of the first
    character field of the line. Clearly this rules is doomed to fail in some
    cases and you can correct it forcing a representation of the line we
    will call a format field. You can go in the main window of sqledit,
    select databases and 'edit sqlkit field' and you will be presented a
    mask to edit the value you prefer.

    .. image:: ../img/sqledit_config.png


filtering
----------

you may have a lot of data and what sqlkit will help you at is to
:ref:`filter <filters>` in a simple way. Each column has a clickable header
that pops a menu entry. The first menu entry pops a filter widget:

.. image:: ../img/filter-panel.png

in the image we have clicked on three column's header: the filter on each
column is composed of 4 parts: the label with the name, the operator for the
filter, the checkbox to disable the filter and the entry for a value.

Some operators have pretty intuitive operators ('>' as bigger than or later
that for dates) text have also regular expression (normally much more
useful so that it's the default) or ``like``.

.. note::
  
   you can select more filter for column, click on the label in the filter
   panel. You can for example say that you want all the films produced
   between 2000 and 2005, that means having 2 filter on the field year.


Pressing ``Enter`` on a field or the reload button will run the query and
present the selected records in the TableView. 

Dates are special in that you often have to filter with dates relative to the
moment you do the query (today, this month,...) so that i added some
shortcuts to accomplish this task (e.g.: 'm' means the beginning of the
month). You can read more on this feature in :ref:`date_filters`.

totals
------

.. image:: ../img/totals.png

One more feature of sqlkit that comes very handy is the ability to make
totals in the fashion of a spreadsheet. This only works on numbers of course,
and you can trigger this feature from the column menu. Since our test
database does not have numbers other than for *year* of production, in the
example I joked and computed the total on the column of the year of production. In real
cases you will do sum with more interesting data...

Subtotals are a very useful feature of any total, so you can ask sqlkit to
create subtotals when some value change (e.g: date, month, year,
director...).

completions
-----------

When you enter data in a text entry or in a foreign key, you may 
find yourself typing something that is already in the database. In this cases
you can have sqledit to search that text for you. Really that's a must for
Foreign Keys where you can only pick the data among those proposed. 

Since the possible values may be a lot and we don't want to wast time
waiting to retrieve data that would only confuse us, we will require sqledit
to show possible values pressing enter in the entry. In this case the text
that we may have already entered will be used to filter the possible values
and to be more precise:

:Shift Enter: will trigger a search using the text at the beginning of the
   field

:Control Enter: will trigger a search using a *regexp*. If you don't know what
   a regexp is, consider that as a minimum it will do a search of the string
   in any position, but can do much more and really also depends on the
   database backend. 

:Control Shift: will disregard what you have already written and do a search
   on all possible values, thus emulating an ``enum`` field.

You can find complete information on how to configure :ref:`completion` in
the docs.

changing view
-------------

When in a table view, you may want to jump on a *mask view* or even keep the
two open simultaneously. That can be simply done by clicking with right
button in a row: the menu that appears lets you edit the row with a mask. If
that's a ForeignKey column you can even edit the value the foreign key points
to.

Mask
=====

.. image:: ../img/mask.png
   :align: right

The other view we can use is the *mask view*. The records are presented by
default in a form with the labels on the right and the forms on the left.

.. note:: 

  This is just a default and the only one possible at the moment, but
  programmatically you can choose any fancy layout you want, but I won't
  digress as I want to limit the information for non developers in his
  context.

completion
------------
In this mask you can see that foreign keys use a combo with a completion
element popdown. Same shortcut as for the table one are used to complete. A
double click on the arrow let you use it as an enum field.

filters
--------

Filters can be activated clicking on the label. the filter panel will be
presented as usual.

The difference is that when the query is issued the result is presented in a
tab of the filter panel and you browse the results clicking in the output
tab or clicking the forward and backward arrows of the mask.


layout
-------

If the table has many fields, you may get a layout that is not very
usable. This is a limit of the interfaces at the moment, not of the sqlkit
package that can handle any fancy layout as you can see looking at the
examples of the demo.

The library also allows you to edit related tables (i.e.: director and
movies) with no effort, in order to do this you need at least a minimum of
programming, namely:

  * defining the model (as per SqlAlchemy)
  * defining the layout  (this is very easy and demo has plenty of examples)

These 2 definitions can be written in the configuration for the a nick of
sqledit, please read :ref:`sqledit manual <sqledit>` for details on nick
configuration.

The Demo
========

The demo is a pretty simple way to be introduced to more advanced features
that you would only have with a little of programming. I hope it will
encourage you to do it and possibly to approach Python.

The very important thing to understand when reading the snippets of the demo
is that each time you write the table as a string (e.g: table='movies') you
will trigger an inspection of the database, but no assumption is made on the
relationships between tables. When you pass a mapper or a class
(e.g. class_=model.Movie) you are passing possibly more information. 

The model in fact (you can go and see in :file:`demo/sql/model/movies.py`)
has lines as::

  class Director(Base):
      __tablename__ = 'director'
      id             = Column(Integer, primary_key=True)
      last_name   = Column(String(60), nullable=False)
      first_name  = Column(String(60))
      nation      = Column(String(6))

      movies      = relation('movie', backref='director', cascade='all, delete-orphan',)

where the last line instructs sqlalchemy of the relation existent between
the tables, and more: it adds an attribute on the class ``Director`` that
holds all the movies produces by that director (and vice verse thanks to the
argument ``backref``).

Adding these information makes it possible to used the layout in a mask to
produce a mask with director and all the movies, if you are interested in
this part... let me know and I will add more info. For the moment I suggest
you to go and read more about :ref:`relationships`

Feedback
========

I hope you found this tutorial useful.

If you like this piece of software, have suggestion on how to improve it or
improve the tutorial I'd be `happy to know`_


cheers
sandro
\*:-)




.. _`download page`: http://sqlkit.argolinux.org/misc/download.html
.. _`pygtk site`: http://www.pygtk.org
.. _`sqlalchemy site`: http://www.sqlalchemy.org
.. _page: http://sqlkit.argolinux.org/sqlkit/filters.html#module-sqlkit.misc.datetools
.. _`web site`: http://sqlkit.argolinux.org
.. _`happy to know`: mailto:sandro@e-den.it
.. _`Windows Package Manager`: http://code.google.com/p/windows-package-manager
.. _download: http://code.google.com/p/windows-package-manager/downloads/detail?name=Npackd-1.14.1.msi&can=2&q=
.. _Python: http://www.python.org/download/
.. _pygtk-all-in-one: http://ftp.gnome.org/pub/GNOME/binaries/win32/pygtk/2.22/ 
.. _sqlkit-VER.zip: http://sqlkit.argolinux.org/download/sqlkit-VER.zip
.. _boundle: http://afb.users.sourceforge.net/zero-install/PyGTK.pkg
