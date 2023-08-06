.. _relationships:

================
Relationships
================

Sqlkit makes editing of data that have relation as one2many or many2many
very simple. It's as easy as adding a field in the layout of the SqlMask::

  lay = """first_name last_name
           o2m=movies      - - -
         """


One2Many in a SqlMak
=====================

This is a very powerful feature of ``sqlkit`` that is built on top of
``sqlalchemy``'s mechanism of properties and session and on the ability of
``layout`` to let you define a widget in a symbolic way.

In the following example we will use a ``SqlMask`` to represent ``Directors`` 
and a ``SqlTable`` to represent films, connected to the first by a OneToMany
relationship.

Suppose you already define a couple of tables in sqlalchemy, we will do it
using elixir_ that slightly simplifies the syntax, in the package the demo
uses declarative layer instead::

   class Director(Base):
       __tablename__ = 'director'
       id             = Column(Integer, primary_key=True)
       last_name   = Column(String(60), nullable=False)
       first_name  = Column(String(60), nullable=False)
       nation      = Column(String(6))

       movies      = relation('Movie', backref='director', cascade='all, delete-orphan',)

   class Movie(Base):
       __tablename__  = 'movie'
       id             = Column(Integer, primary_key=True)
       title          = Column(String(60), nullable=False)
       image          = Column(String(250), info={'render' : 'image', 
                              'base_dir' : './images', 'thumbnail_size' : (30,30)})
       description    = Column(String(512))
       year           = Column(Integer())
       date_release   = Column(Date())
       director_id    = Column(Integer, ForeignKey('director.id'), nullable=False,
			       info={'attach_instance': 'director'})

To get a mask that:
 
 1. lets you see director and films together
 2. lets you edit them adding and deleting at will

You just have to start the SqlMask like this::

  lay = """first_name 
           last_name  nation
           o2m=movies      - - -
         """
  SqlMask(model.Director,layout=lay, ...)


And you will get a mask that looks like this:

.. image:: ../img/o2m.png


delete behavior
----------------

We leave to sqlalchemy the responsibility to decide if a film must be
deleted from the database or must just updated to set the director_id to NULL.
To change this behavior you must act on the cascade property of the
relation (or directly on the database definition). If yo want to delete a
film in stead of just setting the property to NULL you can define the table
in this way::

  
  class Director(elixir.Entity):
      ...
      movies = elixir.OneToMany('Movie', inverse='director', 
               cascade="all, delete-orphan" ### note this line
		      )		
      ...
  

.. _elixir: http://elixir.ematia.de

Filtering
-----------

It is now possible to filter on a field present in related tables, e.g.:
filtering all films that have a certain genre.

.. note::

   Starting from 0.8.6-pre2 filters on a related table are *aliased*
   (see `sqlalchemy docs`_). This is relevant if you filter on related
   table via different path (e.g: filtering staff and manager of a table
   projects, where both staff and managers are a m2m relation to User).

   There are cases where this is really what you want but in some cases this
   is not. Here you really need to deeply understand what is happening
   underneath at the SQL level. As an example if you have a sqlmask of
   directors with a related table of films, if you filter on films and use a
   filter on title (containing 'la') and a filter on year (> 2005), the two
   filters will not be related to the same film: you'll get all directors
   that have a film with 'la' in the title and (possibly a
   different) film produce after 2005. This may or may not be what you want...


Many2many relationship
=========================

many2many relationship are as easy as one2many. Once again sqlalchemy
does the heavy job. Definition is as simple as::


    lay = """year title
             m2m=genres - - -
             """
    tm = sqlkit.SqlMask(Movie.mapper, metadata=__metadata__, 
                        session=elixir.session,layout=lay)
    lay = """
         name 
         m2m=movies -
    """
    tm2 = sqlkit.SqlMask(Genre.mapper, metadata=__metadata__, 
                         session=elixir.session,layout=lay)
      

and will pop up a couple of windows as the following, showing the same data
from the two different main tables: movies with their genres and genres with
they're movies.

.. image:: ../img/m2m.png

adding & completion
-------------------


.. note:: 

  .. versionadded:: 0.8.4
     
  When using :ref:`completion` in a m2m table, adding from completion behaves
  differently that adding from m2o in that it requires the field to be
  already present and does not allow to edit it

  This behavior can be changed setting it's 'm2m_editable' property to
  True (new in 0.8.4)::

     t.related.genres.set_editable(True)

  


..   2. it complains if it cannot get one single element with that value 


Many2One or ForeignKey
======================

Many2One is a simpler case. The table we start from **has** a field that
holds a ForeignKey, we just need to follow it to know the value. This again
happens with no effort at all. In this case it's also possible to use this
field in a filter selection. 

Options 
==========

You can set the field_list directly from the layout as well as the number of 
rows::


   m2m=actors:5:first_name,last_name

will set a 5 rows table, and a field list of ``first_name``, ``last_name``.
The real dimension of the table depends also on the expand attributes of the
containers. you may need to set them to ``gtk.EXPAND|gtk.FILL`` by hand. 
There's an example that demonstrates it.

Behind the scenes
===================

The way sqlkit understands that ``movies`` is an entry point for a
relationship is that it analyzes the ``mapper``, looks for a property with
that name and realizes that it's a PropertyLoader. That means that such an
entry point has been put there by a ``relation``. 


.. _`sqlalchemy docs`: http://www.sqlalchemy.org/docs/05/sqlexpression.html?highlight=alias#using-aliases

