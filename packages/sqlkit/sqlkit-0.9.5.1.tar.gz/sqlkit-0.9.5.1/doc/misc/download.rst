=======================================
 Download, requirements & googlegroup
=======================================
  

Requirements
============

Sqlkit depends on:

       * Python (>= 2.5,  < 3)
       * Pygtk
       * sqlalchemy (>=0.5.4). Rel 0.9.5 is the first sqlkit release
         that works with sqlalchemy 0.7+. 
       * python-dateutils 
       * setuptools
       * the correct driver for your database of choice among the backend
         `supported by sqlalchemy`_
       * babel (localization)

Changelog
===========

this is the Changelog_

.. _Changelog: http://sqlkit.argolinux.org/download/Changelog

Download
========
The code is available under an hg repository::

  hg clone http://hg.argolinux.org/py/sqlkit
  
You can download sqlkit package VER from here_ in tar or zip format. 

+--------------------------------------+-------------------------------------+
| Python package                       |* sqlkit-VER.tar.gz_                 |
|                                      |* sqlkit-VER.zip_                    |
+--------------------------------------+-------------------------------------+


Sqlkit is used in a production environment and great care is put in fixing
any bug as soon as possible. The first stable version has been 0.8.6 in 2008. 

I really appreciate any bug report particularly if based on a repeatable
example, possibly starting from the demo.

Windows
=======

Read the detailed instructions in the tutorial: :ref:`windows-install`.


Debian/Ubuntu
=============

Packages are available, read the :ref:`instructions <ubuntu-install>` on how
to add the repository.

Sqlkit on  Pypi 
=================

Sqlkit is available via Pypi (Python Package Index), so -if you have
already installed setuptools that provides the command easy_install- you can
install it via ``easy_install`` or better ``pip``::

  easy_install pip
  pip install sqlkit

Beware that that will fail if you don't already have PyGTK installed.

You can also install directly with ``easy_install`` that often will fail
understanding already installed packages. Should you have problems with ``pip``
you can revert to::

  easy_install sqlkit

No one of these command will install the backend driver (psycopg2 for
postgresql, MySQLdb for mysql,...) that you are supposed to
install by yourself. Sqlite is included in Python stadard library.


Localization
============

We need the help from some translator to localize in different languages. It
takes some 40 minutes to provide a complete set of translations for each
language. Please visit the launchpad_ 's site or contact me directly.

Author
======

Sqlkit is developed by `Alessandro Dentella`_

.. _list: http://groups.google.com/group/sqlkit
.. _here: http://sqlkit.argolinux.org/download/
.. _Experimental: http://packages.debian.org/experimental/python-sqlalchemy
  
.. _sqlkit-VER.tar.gz: http://sqlkit.argolinux.org/download/sqlkit-VER.tar.gz
.. _sqlkit-VER.zip: http://sqlkit.argolinux.org/download/sqlkit-VER.zip
.. _python-sqlkit_DEBVER_all.deb: http://sqlkit.argolinux.org/download/python-sqlkit_DEBVER_all.deb
.. _sqledit-binary-LNXVER.tar.gz: http://sqlkit.argolinux.org/download/sqledit-binary-LNXVER.tar.gz
.. _sqledit-setup-WINVER.exe: http://sqlkit.argolinux.org/download/sqledit-setup-WINVER.exe
.. _sqlkit-doc_VER_all.deb: http://sqlkit.argolinux.org/download/sqlkiy-doc_VER_all.deb
.. _`Alessandro Dentella`: mailto:sandro@e-den.it
.. _launchpad: https://launchpad.net/sqlkit
.. _`supported by sqlalchemy`: http://www.sqlalchemy.org/docs/dialects/index.html
