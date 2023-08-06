.. _defaults:

==========
Defaults
==========

Defaults are a handy way to avoid typing too much. Defaults are handled by
sqlkit.db.defaults.Default class::

 from sqlkit.db  import defaults
 def_visita = defaults.Defaults('cliente_visita', metadata=db.metadata, local=False)
 def_visita.set_defaults( {'data' : def_visita.now, 'telefonata' : True})
 def_visita.set_default( title='Write a title...', duration=90)
 def_visita.fk('director_id', 'first_name', 'Olmi')


*Defaults* class requires a table name and a metaclass to know where to
autoload/read table definition. 

Defaults can be local to a sqlwidget or global to the application.

set_default
===========

The main method is ``set_defaults`` that
requires a dictionary as argument with *field_name* as keys and *field
defaults* as value. Alternatively ``set_default`` accepts keyword args.

fk
===

Default in foreign key are set literally via ``fk``. It will follow the
reference and find the correct value

now & today
=============

attributes ``now`` and ``today`` will be substituted appropriately when
creating the field


SA defaults & server defaults
=============================

At the moment Sqlalchemy defaults are handled only in case of a fixed value
(not a callable) nor defaults defined in the server. Adding a new record
with an unhandled default will result in an empty value.

.. _local_defaults:

Defaults local to the application
=================================

Sqlwidgets have an attribute called ``defaults`` that is an instance of 
``sqlwidget.db.defaults.Defaults`` already correctly instantiated that allows 
to set defaults local only to the instance of sqlwidget they belong to.

You can use such a default in any of the following ways::

  m = SqlMask('movie', ...)
  m.defaults.set_default(actor=False)
  m.defaults.set_defaults( {'title' : 'write your preferred...'} )
  m.defaults.fk('director_id', 'first_name', 'Fellini')

