==========
 Printing
==========

Sqlkit adds printing capability throught :ref:`oootemplate` module that in turn
uses templates created with Openoffice.org_ and very simple syntax.

In this module 'print' is used in a loose way. In all situations 'print' means
producing a printable file, it can be an ``.odt`` file or a ``.pdf`` one.

.. note:: 

  In a network environment you'll probably use a **remote** server that means
  the file will not be generated locally. Openoffice 3.1 comes with python2.6
  interpreter and uno module even under Windows. So that there's no problem
  using that interpreter or using a different interpreter but pointing to
  it's modules. If you need to have uno modules under windows you can follow
  instructions in this tutorial_ or on stackoverflow_


.. automodule:: sqlkit.misc.printing




.. _psignals:

Signals
========


:context-ready:

   the context has been prepared. You can connect to this signal to add
   element to the context.

   .. function:: context_ready_cb(printtool, context, template_name, sqlwidget):
      
      :param printer: the printing.PrintTool object that emitted the signal
      :param context: the context 
      :param template_name: the template name that is rendered
      :param sqlwidget: the sqlwidget



.. _oootemplate: http://oootemplate.argolinux.org
.. _Openoffice.org: http://www.openoffice.org
.. _stackoverflow:
       http://stackoverflow.com/questions/4270962/using-pyuno-with-my-existing-pythonn-installation
.. _tutorial:
       http://user.services.openoffice.org/en/forum/viewtopic.php?f=45&t=36370&p=166783
