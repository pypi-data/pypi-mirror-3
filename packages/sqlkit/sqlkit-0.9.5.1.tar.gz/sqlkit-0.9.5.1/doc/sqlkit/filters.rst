.. _filters:

=========
 Filters
=========

.. image:: ../img/filter-panel.png
   :align: left

Filtering is a very powerful feature of sqlkit. Any single field in a
SqlWidget may become a filter criteria and many filters on a field are
accepted. A filter panel handles the filters that may also belong to related
table: in that case a join will be built when selecting (read the note on 
selecting through joins in :ref:`relationships`)

As you can see in the image a filter panel gives also the opportunity to
limit the query. Any filter can be enabled or disabled by clicking on it's
toggle.

The result of a filter operation is shown differently in Table or Mask:
Table shows the result directly, Mask shows the list of selected records in
the Filter Panel's Output page:

.. image:: ../img/filter-output.png
   :align:  right

Each record is shown with it's __str__ representation that can be set in the
way described in :ref:`description`.

In this Output Page it's possible to set a field and have records grouped by
that field::

  t.filter_panel.tree = 'field_name'


Filtering Foreign Keys
======================

Filtering works also with foreign keys. In that case the filter acts on the
filter that represents the record, what I call the :ref:`"search"
<completion>` field of the record. In this case the operator used for the
search defaults to regexp/match that in turn uses different operators in
each database backend: '~*' for postgresql, REGEXP for mysql and ILIKE for
the others (well, ILIKE is not present in sqlite but it uses the sqlalchemy
implementation of ilike) adding leading and trailing '%' symbols.

.. note:: **Shortcut**

  As a shortcut to a tipical pattern (pop a filter panel, add a filter for a
  field, set a value, reload), it's possible to write a filter string
  directly in the field and activate the filter/reload operation by
  Control-Alt-f. This will use ``ILIKE`` as search operator and is enabled
  where completion is enabled.


Adding Filters programmatically
===============================

Filters can be added programmatically via method ``add_filter`` that uses
django_like syntax, of interactively. As an example::

  t.add_filter(numeric_field__gte=5, boolean_field=True)
  t2.add_filter(date_field__lte='y', string_field__null=False)

more examples can be found in the :ref:`constraints` sections as they share
the same syntax. Note that a filter can be changed by the user while a
constraint is invisible to him.

filters and join
----------------

When filtering programmatically on a join you must use the field_name as
known by the mapper, i.e. composition of table_name + field_name. Look demo
on join too see how it works::

  t = SqlTable(tables="movie director", dbproxy=db )
  t.add_filter(director_nation='IT') # NOTE director_nation

Here the field *nation* of table *director* is referenced as
``director_nation``

Expressions
===========

Filter work just in the same way for real column as for expressions. 
Example 30 in the demo shows how to create a mapper that have a column with
the number of film  of a director, and you can verify that constraints and
filter work on that table just as any normal column::

  class Director2(object): pass

  ## create the mapper as suggested in the SqlAlchemy tutorial...
  m = mapper(Director2, model.Director.__table__,
     properties={
      'film_number': column_property(
	      select(
		  [func.count(model.Movie.__table__.c.id)],
		  model.Director.__table__.c.id == model.Movie.__table__.c.director_id
	      ).label('film_number')
	  )
    }
  )

  field_list = "last_name, first_name, nation, film_number"
  t = SqlTable(m, field_list=field_list, dbproxy=db)
  t.add_filter(film_number=3)
  t.add_constraint(film_number__lt = 5)

.. _date_filters:

Date filters
=============

Date filters deserve a special chapter. It's very common the need for a
filter based on relative dates (i.e.: the beginning of the month, the year,
the last month and so on), that's the only way to allow saving queries that
will behave the same all the time.

.. automodule:: sqlkit.misc.datetools


.. automodule:: sqlkit.widgets.common.sqlfilter
