.. _completion:

============
Completion
============

.. image:: ../img/completion.png
   :align: right
   
Completion is the way you can avoid writing too much if the system already
has your data. It means you write some text that will be used as filter in a
select statements of all possible values. Completion is active 

* in text fields 
* in foreign key fields
* in many2many fields with :meth:`set_editable(True) <sqlkit.widgets.SqlTable.set_editable>`

This operation has the following main actors: 

  1. the **search field**: the field where what you type is searched for. In
     the image, 'f' is the typed text that will be searched for 
     in the field *last_name* that is the *search_field*. The letter 'f' 
     will be used to filter the output. In this example the first_name
     (Roberto, Federico, Françoise) is not part of the search, but is used
     to better represent the possible matches.

  2. the **object that should be returned**: 
 
     * the *string* to be used (as in enum mode, or in completion in values
       used in the same column). This is only available for char/text fields
       No validation is done by default on this field, the completed text
       can be further edited.

     * the *foreign key* (frequently an ``id``) along with a 
       *representation of the referenced record* (e.g.: the fullname of a
       director). A check is made: there's no way to input a text that is
       not matched on the  remote field (see :ref:`description` below).

     * a *complete record* as when we edit a relation and we use a filter on
       one field but we aim at setting a complete record. E.g.: we select an
       actor from a list and we may be filtering the name or the nation. See
       example 40d.


  3. the **representation of the result**: when using completion on a
     ForeignKey or on an m2m relation, the representation of the possible
     values needs to be taken. In the example of the image 'Fellini' the the
     representation of the referenced record that was referenced by a numeric
     id.

  4. the **operator** used when searching: normally ``regexp`` or
     ``like``. In the image here you see that 'Truffault' is returned that does
     not start with 'F' but *contains* 'f'.


The match of the completion has these *modes*:

  :start: partially written text is used as a filter and completion must
    match from the start of the field. It uses LIKE operator

  :regexp: the match is done via regular expression if db supports it or via
    LIKE operator adding ``%`` on both sides

  :enum: any value matches. All possible values are shown. This mimics an enum
    field. When there are only few values this may result more natural than
    the others 

Since completion implies a search that may return *many* records, it's only
triggered on demand. Normal binding are:

  :shift   Return: triggers 'start' mode completion
  :control Return: triggers 'regexp' mode completion. This is also triggered 
                   pressing the down arrow of a foreign key
  :shift control Return: triggers 'enum' mode 

Pressing ``Alt`` along with the other keys will prevent any
:ref:`filter_completion`

.. _description:

foreign key description & search field
======================================

When displaying data (and data shown by a completion are no exception), a
foreign key is substituted by a more descriptive text. Let's see how to
customize it.

Make sure you understood the limitation on ForeignKey expressed in
:ref:`basic_limitations` 

You can customize the way a record is represented by:

* using :class:`sqlkit.db.utils.TableDescr` class
* writing configuration info in a database table (normally ``_sqlkit_table``)

sqlkit.db.utils
----------------
You would use module sqlkit.db.utils and create an object :ref:`TableDescr`::

  from sqlkit.db.utils import TableDescr
  utils.TableDescr('movie', format='%(title)s - %(year)s', metadata=db.metadata)

metadata is necessary so that TableDescr knows where to go and auto-load
Table to introspect it if you don't provide the search_field (see below)

.. _sqlkit_table:

_sqlkit_table
--------------
It's possible to write in the database the format string to be used in the
table. A table called ``_sqlkit_table`` is searched for (firebird backend
doesn't allow leading '_' in table names so '_'  is stripped for it). 

:search_field:
  The value of this field is used for the search. If no such field was
  defined, the first char field of the tale is used, if it exists.

:format: 
   the value of this field is used to represent the record, e.g.: "%(title)s %(year)s"

You can easily edit this table using :ref:`sqledit`

format and __str__
-------------------

When SqlWidget creates a class on the fly it looks for the 'format' field to
add a __str__ method to the class, so that this representation is used
whenever suitable (e.g.: when a filter action is performed in a Mask)

.. _autostart:

Autocompletion
==============

You can force completion to start after n chars has been entered setting the
completion object ``autostart`` value::

  t = SqlMask('movie', dbproxy=db)
  t.completions.director_id.autostart = 2

Completion will be recalculated every time the written string is shorter that
the last text that triggered the completion.

Take care not to use a little value for ``autostart`` on large tables.

completion and Return in Tables
--------------------------------

There is another situation in which a completion is started
automatically. When editing a foreign key (or an m2m): if a ``Return`` is
hit, a select is issued to check if it's a valid value and if not that value
is used as base for completion. The difference from triggering a normal
completion is that if a valid value is found, no further completion is done.


.. warning::

  Since completion uses the already written chars to filter possible solution,
  if you further delete such chars you are not seeing all the real possible
  solutions but only the already retrieved ones. You can request a new
  completion... 

Group_by
========

There is also en easy possibility to add grouping of completion via a
foreign_key attribute. It's enough to set the group_by attribute of
completion_group_by::

  t.completions.director_id.group_by = 'nation'

.. image:: ../img/completion_group_by.png

.. _`filter_completion`:

Filtering completion
=====================

You can programmatically decide to filter what a completion returns in a
very easy way using :ref:`django like syntax <constraints>` (the same used
to set constraints)::

  t = SqlTable(Movie,...)
  t.completions.title.filter(title__icontains='love')

this line will instruct the completion to only show titles that contain the
world "love".

Filters on a field that is a foreign key will be relative to the related
table::

  # nation_cod is a field_name of the table
  t.completions.director_id.filter(nation_cod='ITA')

will build a constraint on the **director** table filtering only italian
directors. 

If you set relation on your Director class as in::

  class Director(Base):
      ...
      nation_cod = Column(ForeignKey(Nation.cod))
      nation = relation(Nation)

you can set filter on the completion based on this relation::

  ## nation__code (note the double underscore!!!) will trigger
  ## a filter on the cod field_name of the relation nation 
  t.completions.director_id.filter(nation__cod='ITA')
   

dynamic filters
----------------

It's also possible to set a "dynamic filter" i.e. a filter depending on the
value already of another field::

  t.completions.last_name.filter(nation='$nation')

In this case the value of $nation will be set using ``t.get_value('nation')``
In case you have a related table you can go back to the main table::

  t.related.movie.completions.title.filter(director_id='$main.director_id')


enum mode with foreign keys
---------------------------

Enum mode is the way you can mimic a standard enumeration field: you see all
fields independently from what you have in your entry. This is more natural
in some circumstances if you only have few values.

You can get this behavior all the times just hitting
Control-Shift-Return or in ForeignKey fields double-clicking the down arrow.
Since you probably want this depending on the values
of the table you can programmatically choose to serve completion *only* via
this way setting ``force_enum = True`` on the completion::

   t.completions.director_id.force_enum = True

enum mode w/o foreign key
---------------------------

There is another way that mimics enum mode, i.e. setting directly the
possible completion values via the method 
:meth:`set_values <sqlkit.widgets.common.completion.SimpleCompletion.set_values>`::


  t.completions.status.set_values(['open', 'closed', 'waiting for input'])

or::

  t.completions.status.set_values(a_function_that_returns_possible_values)

the signature of this function must be:

.. function:: my_values(value)

   :param value: the value that may have been written in the entry, used to
        filter values, as usual




more customization
-------------------

There are normally 2 possible completion according to the filter level.
An example can better clarify: suppose you have an entry where you are supposed
to enter a username. You set a filter on *active* users, now you need to fix
an old record that really has a user that is no longer *active*. You need to
loosen you filtering criterion momentarily. You can do that Pressing the
``Alt`` key along with normal ``Ctrl-Enter`` or ``Shift-Enter``

These two filtering criteria are stored in two ``session.query`` objects and
are stored in the completion with attributes:

:filtered_query: the query with filters. You set filters on this query with
         ``filter()`` method. If a ``filtered_query`` already_exists,
         filters are added, otherwise it's written from ``query``

:query: the default query, used when no filter is desired (``Alt`` is pressed).
        You set filters on this adding argument "main_query = True" to 
        ``.filter(main_query=True)``. 

Of course each one can be customized with the normal sqlalchemy syntax also.

Note that if you have both filters (with and without main_query option)
order makes difference as ``filtered_query`` is built based on ``query``
when .filter is called for the first time. If you change ``query`` after
calling ``.filter()`` you end up with unrelated filter condition (that's
allowed as you may really want this).


Remember that :ref:`validation` is a completely different mechanism than
completion even if it's not possible to add a field that doesn't come from a
completion.

.. _customizing_description:

customizing description
-----------------------

The ``query`` attribute of the completion determines which fields will be
present in the completions list, the ``format`` attribute decides how it
will be represented. Default value is determined as described 
:ref:`above <description>`, but you can customize it as you prefer, as far
as you use fields present in the query. As an example::

  t.completions.director_id.format = '%(first_name)s %(last_name)s -- %(nation)s'


Behavior on completion with m2m/m2o relationship
=================================================

When the completion is in a SqlTable that represents a not editable m2m
relationship (as ``actors`` would be for ``movies``), the completion does
not simply add the single field but substitutes the whole record.

On such a relationship table's completion you can set filter that will act
on all fields. Rationale: if you have a movie/actor relationship and set a
constraint on actors so that only female should be selected, you probably
want to retain that filter independently from the fact that you select the
nation, the first or the last name.

.. automodule:: sqlkit.widgets.common.completion


