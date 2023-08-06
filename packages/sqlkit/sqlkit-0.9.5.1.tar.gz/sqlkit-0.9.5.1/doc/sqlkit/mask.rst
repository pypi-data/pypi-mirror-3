.. _mask:

=========
 SqlMask
=========

.. image:: ../img/layout-simple.png
   :align: right

layout
=======

The most powerful part of SqlMask is the ability to **define the layout via
simple text description**. In the examples you'll see how easy it is to create
fancy layout that have all nice gtk Widgets like expanders, notebooks, panes
and it makes it incredibly easy to nest SqlTables into SqlMask to build
complex layouts that can also represent :ref:`relationships`.

If you know ReST language and glade, it relates to glade as ReSt to html.

If no layout is provided a flat one will be generated on the fly.

The key is that a textual layout is parsed to see if the token are
recognized as fields of the table that the mask is editing, in which case
introspection is done to understand which widget should be used to edit the
data (according to rules above) and a label is added::

   mylayout = """
      image
      title
      date_release
      TXS=description
      director_id
   """
   m = SqlMask(model.Movie, layout=mylayout, ...)

will creare a mask with an image, an entry, a date a text and a
fkey. ``title`` and ``director_id`` will be already instrumented with
completion: ``director_id`` will try to complete choosing the values of
directors from the ``director`` table, ``title`` will suggest completion based
on title present in the table (and in this case may not be very
useful). ``description`` would render as an entry as it's a *varchar*, we wanted
to "cast" it to *text* using ``TXS=``. 

The description language you can use is pretty rich (and dynamic, so you can
add your custom made widgets): you'd better have  a look at the demo of
sqlkit.layout that you find in sqlkit.demo.layout

When parsing the textual layout, any token that is not recognized as a
field is passed as is to ``sqlkit.layout.Layout`` 


gtk refinements
---------------

Occasionally you may need to refine your layout, change packing, visibility,
attribute an so on. You can reach the gtk widgets via the ``widgets``
attribute of the SqlWidget. In example 26 we use::

  Tbl = t.widgets['T.a']
  Tbl.get_parent().child_set_property(Tbl, 'y-options', gtk.EXPAND|gtk.FILL)

that changes pack properties to a gtk.Table whose name is ``T.a``. If you
have ipython you can start the demo with option -i to gain an interactive
shell to play with an experiment with the widgets. By default each field has
a label whose key in widgets dict is ``l=field_name`` while each entry is
``e=field_name``. 


Shortcuts
----------

:mouse scrolling: allows to browse the records that have been loaded by a
   reload operation
:Control-s:  saves the record
:Control-q:  quits the table
:Control-n:  opens a new record

Signals
========

:pre-display: 

     this signal is emitted when current object has already been set but
     field values have no been set. It can be used to configure custom
     widgets whose appearance may depend on other values.

  .. method:: pre_display_cb(mask, obj)
 
     :param mask: the SqlMask that emitted the signal
     :param obj: the object currently selected or None

.. versionadded:: 0.8.8

.. image:: ../img/mask-demo.png
   :align: right
   :scale: 50%
   :class: preview

.. _save-as:

Save as
=======

Masks have a function *save as new record*, that allows to duplicate a
record (corresponding to table's :ref:`row duplicating <row-duplicating>`). 
It's important you understand exactly what it does so that:

 * it nullifyes the primary key, so that a new one will be generated. If the
   primary key is visible and editable in the mask, it's up to you to delete
   it or change it according to your needs

 * m2m relations: for each *visible* relation, i.e. each relation that is
   shown by the mask **and is of type many to many** it copies the
   records. As an example: actors would be copied in the second film.

   If you want to change the new record in the related table (e.g.: actors)
   do that **only after saving** otherwise you will also change the cast of
   the original film, that's different from other fields as table'mode is to
   save in the same moment you edit.

 * o2m relations: if o2m relations are present a warning is displayed that
   those fields will not be copied **unless you have an on_save_as hook**
   that would mean you are already handling this case. 

   Blindly copying the records would *steal* the references from the other
   record. Just to be explicit: suppose to have a mask of a director with
   his films, the director is Fellini and the film *La strada*. Duplicating
   the record "Fellini" with "Fellini 2" should probably be a 1^st step in
   personalizing some fields. In no way you want to divert the
   ``director_id`` of the film "La strada" that should continue to point to
   the original record "Fellini".

 * visible fields are copied from one record to the other. Please note
   carefully this point: a new empty record is set as current record and
   each visible fields is furtherly saved in the new record. If a field is
   not visible that field will not get copied. You may have problems if
   required fields are not visible. To allow to fill with new values a
   :ref:`hook <hooks>` is invoked named :ref:`on_save_as <on_save_as>`.

.. autoclass:: sqlkit.widgets.SqlMask()
   :members: get_widget, clear_mask, set_frame_label

Introspection of the table is used to determine which widgets will be used to
edit the data. The following rules are applied:

  :varchar: gtk.Entry
     
  :numbers: gtk.Entry with right alignment

  :bool: gtk.CheckBox

  :text: gtk.Text
  
  :FKey: fk_edit (a custom ComboBoxEntry)

  :date/datetime: dateedit (entry + arrow for calendar + time)

  :default: gtk.Entry

All fields will have a label that is sensitive to mouse clicks. A mouse
click pops up a :ref:`filter <filters>` widget.

