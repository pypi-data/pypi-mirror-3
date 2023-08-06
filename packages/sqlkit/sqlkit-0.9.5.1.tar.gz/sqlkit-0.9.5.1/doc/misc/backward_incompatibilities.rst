.. _backward_incompatibilities:

=================================
Backward Incompatibilities
=================================


From version 0.8.6 (first public release) I keep track of backward
incompatibilities:

0.9.3
=====

:requirements: sqlalchemy now needs to be at least rel 0.5.4 as we're using
         AttributeExtension to provide better MVC support

0.9.2
=====

:hooks: ``on__field_change`` now pass also the field. The demo snippet
        already had this arguments but was always None and was not
        documented

:totals: added model, path, iter to ``sum`` method of totals. Impact only on
         customized :ref:`totals`

0.9.1
=====

:hooks: ``on_completion`` is now triggered when you press Return, both for
        tables and masks. Previously was triggered on Return for Masks
        and on click for table.

0.9.0
=====
:Mask: a fix in the layout machinery make setting width specs
       working... that means you may need to fine tune the width of your
       entries. You set the width of an entry as follows::

          last_name:40
	  first_name:30-
	  sex:1>

       the first sets 40 chars, the second sets 30 that would grow to use
       available space, the latter would use 2 chars and would right align
       it (compared to other entries)

:mappers: if a relationship has ``cascade=delete-orphan`` set, and you add
       an object by completion Sqlalchemy will complain that there's a
       missing object. With SA 0.5 this is automatically done, with SA 0.6
       this is no longer supported by sqlkit. You are supposed to
       explicitly add info on the Column as explained in 
       :meth:`sqlkit.fields.ForeignKeyField.add_related_object`


0.8.7
=====

:Table:
  
  *  ``self.current`` points to ``self.get_current_obj()``, no longer
     ``get_selected_obj()``

  *  button-press-event now has one more argument: treeview. This is
     necessary due to the fact that table now have views and t.treeview only
     points to the main view's treeview.

:Table & Mask:

  * now keyword table/class/mapper are deprecated in favor to setting it
    as first argument.

:Hooks: 

   arguments in hooks of related widgets where not as documented: a hook on
   a sqlwidget acting on a related  widget would receive the related widget
   as first argument rather that the main one. Look at the the following case::
   
     lay = """
	user
	o2m=addresses
     """
     class Hook(object):
	def on_change_value__addresses__domain(self, sqlwidget, field_name, value, fkvalue):
	   pass

     m = SqlMask(User,... hooks=Hook())
     m_address = m.related.addresses
     
   the hook instance will receive ``m`` as argument where previously
   received ``m_addresses``


