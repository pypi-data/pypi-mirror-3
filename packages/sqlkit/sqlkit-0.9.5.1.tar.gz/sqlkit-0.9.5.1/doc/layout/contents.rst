=========================================================
Layout GUI built on the fly  - A GUI description language
=========================================================

This is **the key** of the mask widget and is really what makes writing a layout
with SqlMask so easy.

If you know what **glade** or other gui builder are, think at this part as the
"markup sistem" for html language.

Using this description language to define a layout we try to use as little
writing as possible, we are asking sqlkit to guess all the properties that
it can from the name.

What can be guessed? A lot!!!

Imagine you have a table with movies, and a field is title, anoter is
director_id. The database knows that the first on is a varchar and the
second is a foreign key. It **can** guess how you will want to represent it
so that you will just need to you thei're name in drawing the layout::

   title  director_id

The biggest gain we have when setting :ref:`relationships` between tables.

The code of the layout package and probably the definition of the language
itself is deemed to be rewritten, as was the first step into python in 2005,
but it proved to behave well in these years. After looking at te ReST markup
syntax I am tempted to rewrite the language in a simpler way.

.. toctree::

   layout
