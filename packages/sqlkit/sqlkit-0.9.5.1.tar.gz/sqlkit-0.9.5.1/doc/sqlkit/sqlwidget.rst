============
 Sqlwidget
============

This is the base class for :ref:`mask` and :ref:`table` that implements the
common interface. 

mandatory argument
==================

The first and mandatory argument is the ``mapper`` of the object that will
be retrieved and displayed. Alternatively any other objects from which the
sqlwidget infers them (e.g.: the tablename and the metadata where the table
can be autoloaded):

* a mapper
* a mapped class
* table name (requires you also pass metadata)

In older releases different options: ``class_``, ``table``, or ``mapper``
where used. Now a DeprecationWarning is raised if you use those opts.

main options
============


Any sqlwidget needs a ``session`` as well. 

Metadata is also used when auto-loading tables referenced by foreign keys to
display a better representation of the referenced record.

.. _dbproxy:

dbproxy
-------

Since a typical scenario is to have to provide a session different in each
SqlWidget and a metadata, an object is provided -``dbproxy``- that can be
initialized from the engine specification::

  from sqlkit.widgets import SqlMask, SqlTable
  from sqlkit import dbproxy
  db = proxy.DbProxy(engine="sqlite:///model/movies.sqlite")
  SqlTable("movies", dbproxy=db)

below you can see some alternatives that would work as well::

  Session = sessionmaker(bind=self.metadata.bind, autocommit=False)
  sess = Session()
  meta = MetaData()
  meta.bind = "sqlite:///model/movies.sqlite"
  #
  SqlTable("movies", session=sess, metadata=meta)

  # passing a mapped class (Movie here is build with declarative layer):
  # the metadata is found from the mapper.local_table.metadata

  SqlTable(Movies, session=sess)

Session are created with  ``autoflush=False``, ``expire_on_commit=False`` but
can be changed when building ``DbProxy``. 

Since version 0.8.6 default value for *autocommit* has been turned to  *True*
to prevent `idle in transaction`_ in postgresql.


session & expire_on_commit
==========================

The reason to have ``expire_on_commit=False`` is that if you don't set it,
after every commit, you have to reload all objects and the interface turns
very slow, especially when working with a remote database.

``expire_on_commit`` is a recent addition to sqlalchemy session (around sa
rel. 5.03rc) so I try it and fallback to default that would turn to be
slower. Previous 0.5 rel called it ``autoflush``

.. autoclass:: sqlkit.widgets.common.sqlwidget.SqlWidget(see_below)
   :members: __init__, add_constraint, add_filter, resize, set_records,
             set_format, is_mask, is_table, sb, get_value, set_value,
	     get_current_obj, set_mode, add_temporary_item, reload, commit,
	     add_validation_error, add_not_null_error


Attributes
===========

.. attribute:: filter_panel

   The :ref:`filter_panel` widget

.. attribute:: related

   a container for all related sqlwidgets (i.e.: SqlWidgets that have a
   relation with this sqlwidget defined by sqlalchemy and that are 
   displayed in the widget).

   This is used in all situation in which you need to fine-tune the
   configuration of a related table (completion, layout, ...)

.. attribute:: completions

   a container of all completion objects. Needed to change the behavior of
   some completion (see :ref:`completion`)

.. attribute:: gui_fields

   a container for all validation fields. A validation fields is an object
   that lives in ``sqlkit.fields`` and that knows how to represent a field
   and how to validate it.

.. attribute:: gui_field_mapping

   A dict used to force a map between a ``sqlkit.Field`` and a gui
   field. Read more in :ref:`fields`.

.. attribute:: query

   the sqlalchemy query object (``session.query(mapper)``) with all
   constraints applied. Can be manipulated as necessary as long as it stay a
   query object.

.. attribute:: layout

   the layout definition for this SqlWidget. This is the used definition for
   SqlMask while for SqlTable is only used if the record is opened in SqlMask
   (right click on the record in SqlTable).

   You can also set it on a related table::

      GUI="director @ m2m=movies"
      t = SqlMask(Director, layout=GUI, ...)
      t.related.movies.layout = "title @ m2m=actors"
   

.. attribute:: lay_obj

   the sqlkit.layout.Layout object used to create the layout

.. attribute:: current

   the object represented by a mask or a possible selected record in a table
   or None. In :class:`SqlTable <sqlkit.widgets.SqlTable>` in the transient
   in which you are saving a record in a table (when selection changes)
   ``self.current`` will point to the obj that is to be saved (while the
   selected object may already be another one).

.. attribute:: field_list

   a list of the field names the GUI is handling. It comprises
   PropertyLoaders (i.e. properties of the class that act as a loader of
   other info - all relation are seen as PropertLoaders w/o column)

.. attribute:: order_by

   an order_by string or clause element. Same as parameter passed to the
   class. It's a property, can be set in any moment.


.. attribute:: session

   the sqlalchemy session used for querying

.. attribute:: defaults

   an instance of ``sqlkit.db.defaults.Defauls`` instantiated with
   local=True as explained in :ref:`local_defaults`. Any default set with
   this instance will only be visible in this sqlwidget.

.. attribute:: title

   the title of the Window.

.. attribute:: mode

    the mode describing permissions of the widget. See :ref:`set_mode <set_mode>`

.. attribute:: noup

    noup can be a set of field_name or a comma separated string with possible +- sign
    to add/remove field_names to the set of field_names that will not be possible to update

    Note that to add a non editable field_name you must used '+field_name'. Using simply 'field_name'
    will reset the list to only  that field_name

.. attribute:: actiongroup_* 

    see :ref:`uimanager`

.. attribute:: ui_manager

    see :ref:`uimanager`

.. attribute:: relationship_leader

   Th case this sqlwidget is representing a relation of a SqlMask, that
   SqlMask is referred to as a relationship_leader.
    
.. _sqlalchemy: http://www.sqlalchemy.org

  
.. _signals:

Signals
========


:pre-display:
   A record is about to be displayed.

   .. function:: pre_display_cb(sqlwidget, obj):
      
      :param sqlwidget: the widget that emitted the signal
      :param obj: the object that is about to be displayed

:record-selected:
   A record has been displayed in Mask or selected in Table.
   The callback will just receive the widget as argument.

   .. function:: records_selected_cb(sqlwidget):
      
      :param sqlwidget: the widget that emitted the signal

:record-saved:
   A record has been saved. This signal is *not* emitted from within session
   extension. That means you are sure there will be just one signal for each
   button press on "save" button. This is issued from within the :meth:`SqlWidget.commit`
   method independently from the fact that a real modification occurred, so
   you are not guaranteed any modification took place. Was originally added
   to implement a destroy of the widget when the save operation was performed.

   The callback will just receive the widget as argument.

   .. function:: record_saved_cb(sqlwidget):
      
      :param sqlwidget: the widget that emitted the signal

:record-new:
   A new record has been added. 
   The callback will just receive the widget as argument.

   .. function:: record_new_cb(sqlwidget):
      
      :param sqlwidget: the widget that emitted the signal

:record-deleted:
   A record has been deleted. 
   The callback will receive the widget and the obj.

   .. function:: record_new_cb(sqlwidget, deleted_obj):
      
      :param sqlwidget: the widget that emitted the signal	
      :param deleted_obj: the obje that was deleted

   Note that this signal is emitted only for records deleted explicitly,
   i.e. records that where the ``current record`` in a mask/table. If a
   record is deleted as a side effect (e.g.: becouse cascade="delete-orphan"
   is set) no signal is emitted for that obj.


:records-displayed:
   Records have been displayed. This may be after :meth:`SqlWidget.reload`
   or :meth:`SqlWidget.set_records`.
   The callback will just receive the widget as argument.
   See also :ref:`context changed <context_changed>` to see another signal
   that better tracks *any* change

   .. function:: records_displayed_cb(sqlwidget):
      
      :param sqlwidget: the widget that emitted the signal

:after-flush:
   flush has occurred, normally commit should not add any errors. This is
   implemented with a SessionExtension: if you used the default session
   obtained via get_session() you are assured that it will be correct. If you
   create a session by yourself, be sure to add ``sqlkit.db.proxy.SKSessionExtension`` to the
   session extensions or you won't have this signal. Read more detailed
   explanation in :ref:`hook on_after_flush <on_after_flush>` 

   .. function:: after_flush_callback(sqlwidget, object, session)

      :param sqlwidget: the sqlwidget that emitted the signal
      :param object: the object that was *current* when session was
	  flushed. Current means that it was the main object represented. Many
	  other widgets may be present, possibly in "dirty state", "new" or
	  "deleted", but current was the one selected in a table or displayed in
	  the main mask
      :param session: the session that was flushed. The moment in which the signal is
	  emitted you can still dig into ``session.dirty``, ``session.new`` 
	  and ``session.deleted`` and find which attributes have been changed
	  (you may want to use :func:`get_differences`)

:after-commit:
   run from within ``after-commit`` SessionExtension. Callback signature is
   identical to ``after_flush_callback`` above.
   
:delete-event:
   emitted when the sqlwidget is destroyed

   .. function:: delete_event_callback(sqlwidget)

      :param sqlwidget: the sqlwidget that emitted the signal

.. _hooks:      

Hooks
=====

Beside signals there is another way to add controls: hooks. A hook is a
function that will be called in particular moments only if present. 

Hooks are the main way to customize the behavior of a sqlwidget.  Some of
the hooks (``on_validation.*``) are related to validation other are related
to configuration (``on init``), others (``on_activate``) may be used to save
typing.

Hooks are searched for in the methods of the instance of a class declared in
the optional ``hooks`` argument or in the global registered hooks (see below).

Hooks can be *registered* using :func:`sqlkit.db.utils.register_hook` (and
:func:`get_hook <sqlkit.db.utils.get_hook` from :ref:`utils <dbutils>` module)
so that any sqlwidget built on that table will use those hooks (unless the
table is part of a join or another selectable!!). The advantage is that
browsing data (e.g. using right click on a table row) can lead to opening
tables that are not configured: registering hooks is a way to enforce
configuration (and possibly constraints) on any widget.

As layout hooks can be registered with a nick (default is ``default``) so
that you can register different hooks for different editing flavors. E.g/:
you can have a table for *people* and you can decide to open it with *customer*
or *provider* layout/hooks just registering both layout and hooks and using
argument ``layout_nick``.

Use it with care as it may lead in situation in which not all fields are
present (due e.g. to a different layout or different field_list)

The following hooks are defined:

:on_change_value__field_name: this hook is used to trace *changes* in the
    widget. It's mainly meant to be used interactively but it is also
    triggered when :meth:`set_value
    <sqlkit.widgets.common.sqlwidget.SqlWidget.set_value>` is invoked with
    initial=False. It's **not** changed if the value is set on record
    change.

    Currently it behaves differently for Table widgets or Mask widgets.

    Mask widgets invoke it each meaningful changes i.e. each char for
    varchar/int field, each time a value is choosen for enum/foreign key
    fields,  when a date is selected or validated for Date widgets. 

    Table widgets invoke this hook only when the field is leaved or
    activated (Return is pressed).

    .. note:: Implementation of this hooks is currently limited to some
              fields: Varchar, Int, Float, Numeric, Enum, ForeignKey, Date,
	      DateTime, Bool. Text, Images, Time and Interval are not
              implemented. Example 63c is a complete example that shows it.

    .. function:: on_change_value__field_name(sqlwidget, field_name, value,
                  fkvalue, field)

       :param sqlwidget: the sqlwidget (SqlMask or SqlTable) that runs the hook
       :param field_name:  the field_name
       :param value:  the new value
       :param fkvalue: if field is a ForeignKey or enum, the displayed value
       :param field: the field

.. _on_completion:

:on_completion__field_name: called when a completion 
    is chosen

    .. function:: on_completion__field_name(sqlwidget, field_name, obj)

       :param sqlwidget: the sqlwidget (SqlMask or SqlTable) that runs the hook
       :param field_name:  the field_name

       :param obj: the matched object in the completion. This obj has
       	      attributes for each *field_name* named in :attr:`attrs
       	      <sqlkit.widgets.common.completion.SimpleCompletion.attrs>`
       	      attribute of the completion. You can add field_names to
	      that attribute if you need them in this hook function::

	        sqlwidget.completions.director_id.attrs += ['nation']
		
	      allows you to add a completion hook::

 	        def on_completion__director_id(self, sqlwidget, field_name, obj):
 	            print obj.nation
        	    sqlwidget.set_value('nation', obj.nation)

              you can also reach field attributes as dict values: obj['nation']. 
   
.. _on_save_as:

:save_as:

     .. versionadded:: 0.9.3

     this hook is invoked each time a record is saved as a duplicate of
     another one. After the new record is filled and before it's saved you
     can customize at your will. Callback function:

     .. function:: on_save_as(sqlwidget, old, new):

        :param sqlwidget: the mask/table that invoked the hook
	:param old: the old object that was copied 
	:param new: the new object 

     When this hook is present, no warning on how the copy is handled is
     raised as it's considered that the programmer has already coped with
     all the tricky issues.

:on_validation: called when all the values have been collected in the object,
    before calling validation on all fields and related widgets. That's a
    good point to implement any procedure to add automatism's. Within this
    hook you can propagate errors to the validation machinery in two of ways:

    1. raising ``sqlkit.exc.ValidationError``. Simple when just one error is
       found
    2. filling self.validation_errors: a dict holding all errors. The *key* is
       the field_name or "record_validation", the value a list of error messages
    
    .. function:: on_validation(sqlwidget)

       :param sqlwidget: the sqlwidget (SqlMask or SqlTable) that run the hook

.. _on_field__validation:

:on_field_validation__field_name: called to validate a single field
    as for the previous ``on_validation``. This is called from within the
    :meth:`field's validation method <sqlkit.fields.Field.validate>` 

    1. raising ``sqlkit.exc.ValidationError``. Simple when just one error is
       found
    2. filling self.validation_errors: a dict holding all errors. The key is
       the field_name or "record_validation", the value a list of error messages
    
    .. function:: on_validation(sqlwidget, field_name, field_value, field)

:on_activate__field_name: when *Return* is pressed in Mask or Table. Good to
    complete fields via calculation on other fields (e.g.: total, vat...).
    The name derive from the GTK name 'activate' that is when you press
    'Return' in an entry, even thought in a Table's treeview it's really
    connected to the cell's ``edited`` signal (limited to Varchar and
    Numeric columns).

    .. function:: on_activate__field_name(sqlwidget, field_name, field)

       :param sqlwidget: the sqlwidget (SqlMask or SqlTable) that run the hook
       :param field_name:  the field_name
       :param field:  the ``sqlkit.widgets.common.field``
    
:on_init: run as the last command of __init__. It's main purpose is to 
    allow to configure a widget in a way that will be handed over to a
    possible SqlMask generated right-clicking from a table row (see :ref:`recordinmask`).


    .. function:: on_init(sqlwidget)

       :param sqlwidget: the sqlwidget (SqlMask or SqlTable) that run the hook
   
.. _on_pre_layout:

:on_pre_layout: run before the layout is setup. It's main purpose is to 
    allow to add fields in :attr:`gui_field_mapping` (that is only useful for
    SqlMask). Note that you can force a field for a table's attribute if you
    want setting info's *field* key pointing to that field's class.

    .. function:: on_init(sqlwidget)

       :param sqlwidget: the sqlwidget (SqlMask or SqlTable) that run the hook
   

.. note:: **Hooks invoked within the session extensions**

      The hooks that are called from within the session extensions, can be
      called **several times** if there are more sqlwigets sharing the same
      session (that happens for example each time you open a mask to edit
      the row of a table i.e.: :ref:`recordinmask`)

.. _on_after_flush:

:on_after_flush: 

    run as the signal with the same name from within ``after_flush`` 
    session extension method.

    This hook is completely similar to ``after-flush`` signal, but is meant
    to be defined in a separate class so that it's easier to propagate
    validation hooks to a spawned child (i.e.: :ref:`recordinmask`, when
    opening a mask by right clicking on a table record). You'll see that
    ``on_after_flush`` is called eather.

    From the sqlalchemy documentation: "Note that the session's state is
    still in pre-flush, i.e. *new*, *dirty*, and *deleted* lists still
    show pre-flush state as well as the history settings on instance
    attributes". This is true for *after_commit* hook as well, it is not true
    for *after_flush_postexec*, that on the other had has already setup
    relation.

    I end up in some circumstances to split the callback in two phases: one
    that detects if an action is needed from within the
    after_flush/after_commit phase, the second (may be a mail, or any other
    action) from within the :ref:`hook on_record_saved <on_record_saved>`,
    so that I can use the relations. Beware that you may have one call to
    ``on_after_flush`` and more different calls to ``on_after_commit``

    .. function:: on_after_flush_callback(sqlwidget, object, session)

      :param sqlwidget: the sqlwidget that emitted the signal
      :param object: the object that was *current* when session was
	  flushed. Current means that it was the main object represented. Many
	  other widgets may be present, possibly in "dirty state", "new" or
	  "deleted", but current was the one selected in a table or displayed in
	  the main mask
      :param session: the session that was flushed. The moment in which the signal is
	  emitted you can still dig into ``session.dirty``, ``session.new`` 
	  and ``session.deleted`` and find which attributes have been changed
	  (you may want to use `get_differences`), but you won't have
          correctly setup relation's object

:on_after_flush_postexec: run as the signal with the same name from within
    ``after_flush_postexec`` session extension method.

    As in the precedent hook this is called exactly within the session
    extension method by the same name. When it's run the session will have
    no longer information on session.dirty/session.new/session.delete but
    will have all relations set-up.

    The callback has the same signature as for :ref:`hook on_after_flush <on_after_flush>`

:on_after_commit: run after commit
    after_commit session extension method
        
    The callback has the same signature as for :ref:`hook on_after_flush <on_after_flush>`

.. _on_record_saved:

:on_record_saved: run from within the commit method of the widget, that
    assures that will be issued just once. It's just equivalent to the
    signal with the callback has the same signature:

   .. function:: record_saved_cb(sqlwidget):
      
      :param sqlwidget: the widget that emitted the signal


Hooks for related widgets
-------------------------

If you need to add hooks for related sqlwidgets (those that display related
records as explained in :ref:`relationships`) you need to add the
relationship_path in the method name, i.e. the value you have used in the
table definition for the relation (and in the layout as in m2m=actors)

.. _wav_example:

example
+++++++

This example shows how to use hooks to play a sound on completion::

  class Hook(obj):
      def on_completion__genre(self, field_name, obj):
           if obj.genre == 'horror':
	        play('horror.wav')

  MovieMask(class=models.Movie, hooks=Hook(), ...)


Registered hooks and SessionEtensions
-------------------------------------

When hooks are :ref:`registered <dbutils>` their customizations are
enforced each time the model for which they're registered is called. That adds
some complications you should be sure to understand if using one of these
hooks:

 * on_after_flush
 * on_after_commit
 * on_after_flush_postexec

These hooks are called within a SessionExtension that calls hooks on any
sqlwidget that may be using the same session. An m2m, m2o relation table
share the same session as the Mask that holds them so that it's pretty
normal to have several different tables within the same session.

From the SessionExtension hooks are searched for in any of these so that you
should write the hooks keeping in mind it can be called from another
sqlwiget's commit.

As an example, suppose you have a Mask with the following layout::

   first_name
   last_name
   m2m=genres   m2m=actors

suppose *movies*, *genres* and *actors* have registered ``on_after_commit``
hooks. They will all be called on any commit. Adding a genre object will
trigger *on_after_commit* on the Actor's table and vice verse.







.. _diff:

get_differences
---------------

Module :ref:`sqlkit.db.utils <dbutils>` provides a simple function that yields
all modified attributes of an object, along with their old and new values

.. function:: get_differences(obj)

   :param obj: the object to be inspected
   :param session: the session the object belongs to
   :rtype: field_name, old_value, new_value. Old value and new value are lists.

.. function:: get_history(obj, field_name)

   :param obj: the object to be inspected
   :param field_name: the field_name 
   :param session: the session the object belongs to
   :rtype: new_value, unchanged_value, old_value, . Old value and new value
       are lists. The order is different from ``get_differences`` as this is
       exactly what is returned from the SA function


Saving varchar and text fields
==============================

Text fields with empty values will be saved as NULL. To change this
behavior you need to set blank=True on fields::

  t.gui_fields[field_name].blank = True



.. _`idle in transaction`: http://groups.google.it/group/sqlalchemy/browse_frm/thread/6abb815a3728d41c?hl=it&tvc=1&q=idle


.. _uimanager:

UiManager: menu and actions
===========================

Menu entries are handled via standard gtk.UiManager interface. One interface
is created for each toplevel Window and for each :ref:`view <views>` in a SqlTable
widget. You can see some examples in the demo (70-72).

Standard actions are divided into the following categories::

  General (self.actiongroup_general)
       PendingDifferences
       Quit
       Go
       Modify
       Tools
       File
       Help
       About
  Table (self.actiongroup_table)
       HideColumns
       ShowColumns
       Records
       MaskViewFKey
       Export
       MaskView
       Zoom-fit
  Insert (self.actiongroup_insert)
       New
       Save-as (just for SqlMask)
  Delete (self.actiongroup_delete)
       Delete
       RecordDelete
  Update (self.actiongroup_update)
       Save
       Undo  (just for SqlMask)
  Browse (self.actiongroup_browse)
       Filters
       Reload
  Select (self.actiongroup_select)
       Back
       Forward
  Print (self.actiongroup_print)
       Print
  Debug (self.actiongroup_debug)
       Gtk-tree


While for each table's view you have::

  Table
       HideColumns
       ShowColumns
       Records
       MaskViewFKey
       Export
       MaskView
       Zoom-fit
  Insert
       New
  Delete
       Delete
       RecordDelete

Changing an entry
------------------

To change an entry you can: 

#. add an actiongroup in which you have defined an  action with the same
   name 
#. insert this actiongroup *before* it's relevant one (position 0 is
   normally a good choice

Example #72 in the demo shows how to do it

Adding an entry
---------------

the standard way is shown in demo snippet #70:

#. create an xml definition and add it to ui_manager
#. create an action and add it to an actiongroup

You can also use a SqlTable method :ref:`add_temporary_item <add_temporary_item>` that will add a
temporary entry, so that it can be contextually changed. This way is
demonstrated in demo snippet #71
