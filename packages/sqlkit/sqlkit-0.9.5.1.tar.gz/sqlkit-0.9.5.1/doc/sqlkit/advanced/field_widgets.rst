.. _field-widgets:

=============
Field Widgets
=============

Each field is represented using a proper gtk widget. Table and Mask need two
different objects, a cell renderer for tables and a widget from module
sqlkit.widgets.mask.miniwidgets for masks.

Cell renderers and function to represent the data are defined in
sqlkit.widgets.table.columns.

Widgets defined in sqlkit.widgets.mask.miniwidgets are just interfaces (or
proxies) to other gtk widgets.

.. automodule:: sqlkit.widgets.mask.miniwidgets

.. automodule:: sqlkit.layout.image_widget

.. automodule:: sqlkit.layout.dateedit
