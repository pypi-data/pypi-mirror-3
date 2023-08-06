# Copyright (C) 2009-2010-2011, Sandro Dentella <sandro@e-den.it>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
.. _oootemplate:

=======================
OpenOffice.org template
=======================

This module makes it possible to use an oasis ``.odt`` document as a template to produce
documents via the use of an openoffice server (i.e. an istance of openoffice that
listens for connections by clients).

It uses the uno module that comes with openoffice. In the following image you can see
how the template looks before rendering and how the ``pdf`` produced looks.
The red circle stresses the marker that makes the template produce many lines for each
input line: one for each object in context.

.. image:: ../img/ootemplate-colors.png

This rendering can be obtained by code very similar to this :ref:`example`

The template
============

An openoffice writer document (``.odt`` extension) can be used as template.  No
particular templating skills are required by the template designer, just
ability to create an openoffice document and a list of variable's names that
must be used. Clearly this list must be provided by the programmer to the
designer.


scenario
--------

oootemplate will substitute variables values where needed. ::

  Dear Mr. $user.name $user.last_name,

  Today $date we  received an order for $n books:

  +-----------------------------+----------------+----------+----------+
  |Title                        |Author          |N. pieces |$currency |
  +-----------------------------+----------------+----------+----------+
  | ++$title                    |$author         |$qty      |$price    |
  +-----------------------------+----------------+----------+----------+


This is an example of a template rendered as possible with ascii art.

There are 2 different substitutions that can be done:

 a. simple substitutions ($user, $date, $currency, above - yellow in the image)
 b. multiline substitutions (the book entries above, starting with ++ - green
    in the image)

the first refers to substitution of a single value that is already present in
the document,  the second refers to the insertion of several
rows according to a list of fields that are probably in a table.


The variables defined in the table should be repeted in loop for each book
provided in the ``context``, that implies an increment of the number of
rows of the table. The expected output resembles what follows::

  Dear Mr. Alessandro Dentella,

  today June, 2 2008, we received an order of 2 books:

  +-----------------------------+----------------+----------+----------+
  |Title                        |Author          |Copies    |Euro      |
  +-----------------------------+----------------+----------+----------+
  | Q                           |Luther Blisset  |1         |10        |
  +-----------------------------+----------------+----------+----------+
  | Il sistema periodico        |Primo Levi      |2         |8         |
  +-----------------------------+----------------+----------+----------+

As for any template system a special syntax is needed to allow people to
create loops. We are constrained to what can be done by a simple user of
openoffice (no programming at all) so we choose to use a MULTI_LINE_MARKER
in the default form of a '++' (red circle in the image) .

To make things more complicated it's clear that the person that created the
template (the .odt document), may have used a table just for formatting
reason so that substitution of type a. can be in an openoffice table or not.

implementation
---------------

Substitution of type ``a.`` above are done using search and replace
functionality of openoffice API, while substitution of type ``b.`` are
implemented as a loop on table's rows and cell in 2 different ways: one that
preserves the style of each word of the cells and one that doesn't.
The former uses getTrasferable() method on each cell and is slower.

You can switch from one to the other setting Template's attrribute
:attr:`Template.preserve_styles`

The pattern used to detect what is a table can be customized. While the default
is '$' as in the shell or in python template system (and perl and php...) since
you may have the '$' symbol in your document you may want to customize it. See
Template's method ``set_pattern``.

context
-------

The context is the object that contains the mapping variable/value to be used.
It needs an argument -a dict- that holds the values.

oootemplate allows you to have more that one tables in your document. That means
you can implement easily things as::

  Dear Mr. $user.name $user.last_name,

  you can order these books at 20% discount

  +-----------------------------+----------------+----------+----------+
  |Title                        |Author          |N. pieces |$currency |
  +-----------------------------+----------------+----------+----------+
  | ++$title                    |$author         |$qty      |$price    |
  +-----------------------------+----------------+----------+----------+

  or these books at 50% discount

  +-----------------------------+-----------------+----------+----------+
  |Title                        |Author           |N. pieces |$currency |
  +-----------------------------+-----------------+----------+----------+
  | ++$title                    |$author          |$qty      |$price    |
  +-----------------------------+----------+------+----------+----------+
  |Title                        |Author    | Extra|N. pieces |$currency |
  +-----------------------------+----------+------+----------+----------+
  | ++$title                    |$author   | $x   |$qty      |$price    |
  +-----------------------------+----------+------+----------+----------+

In this example we have 3 lines that start with ++, that means that will be
conseidered prototipes for new lines. For each of these 3 rows there need
to be a list of objects (books in the example) in the context.

Since Openoffice-org tables have names, we wil use that name as a key in the
context for the value. That's enought for the first table (20% discount) not
for the second where we have 2 lists in a table. To cope with this case, we
can put as value a dict with entry an integer that indicates the position
starting from 1 (see example below)


name mapping
~~~~~~~~~~~~

Occasionally the name of the variable will be too long to fit in the space
that you want to allocate. You can translate a shorter name to the real
name in the dict context.translate (see example in the demo), blue circle
in the image.

This way you can hide the complexity of some variable name. Note that you
can translate both ``$rs.manager.address`` in ``$addr`` or
``$director.last_name`` in ``$d.last_name``.

output
------

All output accepted by openoffice filters, you're probably using ``.odt`` or ``.pdf``

.. _example:

example
-------

A tipical sample code is::

   import ooootemplate as oo

   tmpl = oo.Template('/tmp/mytemplate.odt', server='127.0.0.1', port=2002)
   context = oo.Context({
       'user' : user,
       'date' : date(2008, 6, 2),
       'currency' : 'Euro',
       'Table1' : (book1, book2, ...)  # lazy assignement (simple tuple)
       'Table2' : (
            (book21, book22, ...),     # correct assignement (list of tuples)
            (book31, book32, ...),
            )
       })

   tmpl.render(context)
   tmpl.save_as('/tmp/new_document.pdf')

API
=======

Context
-------
.. autoclass:: Context
   :members: __init__

Template
--------

.. autoclass:: Template
   :members: __init__, render, save_as, set_pattern, VARIABLE_PATTERN, VARIABLE_PATTERN_OO,
             MULTI_LINE_MARKER, document,  oo_context,  search, preserve_styles

Table
-------
.. autoclass:: Table
   :members: __init__


.. autoclass:: TableWithStyles
   :members: __init__

"""

import os
import re
import sys
import datetime
from subprocess import Popen, PIPE
import warnings
import socket

import uno
from com.sun.star.beans import PropertyValue

NoConnectionException = uno.getClass("com.sun.star.connection.NoConnectException")
OutOfBoundsException = uno.getClass("com.sun.star.lang.IndexOutOfBoundsException")
IllegalArgumentException = uno.getClass("com.sun.star.lang.IllegalArgumentException")
class WrongTemplateName(Exception): pass

#class OOExecuteException(Exception): pass

# VARIABLE_PATTERN = re.compile("(?P<match>__(?P<var_name>[^ ]+)__)")
# VARIABLE_PATTERN_OO = "__[^ ]+__"
# MULTI_LINE_MARKER = '\+\+'  # a re.match pattern i.e. starts from beginning of string

def start_oo(server="127.0.0.1", port=8100, headless=False):
    """
    Starts OpenOffice.org with a listening socket.

    :param server: a server name
    :param port:   the port to connect to
    :param headless: if False, disables the headless mode.
    """
    # there's a class implementing all this here:
    # http://www.linuxjournal.com/content/starting-stopping-and-connecting-openoffice-python
    # binary name to invoke
    ## get oofice or libreoffice. This works on linux only, I guess
    ooffice = Popen('which ooffice', shell=True, stdout=PIPE).communicate()[0] and 'ooffice'
    libreoffice = Popen('which libreoffice', shell=True, stdout=PIPE).communicate()[0] and 'libreoffice'
    program = ooffice or libreoffice
    # basic options needed
    opts = ['-accept="socket,host=%(server)s,port=%(port)s;urp;StarOffice.ServiceManager"' % locals()]
    opts += ['-norestore', '-nologo', '-nocrashreport'] #  -invisible
    if headless:
        opts += ['-headless']

    if re.search('libreoffice', program):
        ## libreoffice has correctly deprecated -norestore in favor of --norestore & Co.
        opts = ['-' + opt for opt in opts]
    cmd = " ".join([program] + opts)
    Popen(cmd, shell=True) 

def connect(server='127.0.0.1', port=8100, headless=False):
    """
    connect to server, returning the oo_context

	:param server: a server name
	:param port:   the port to connect to
	:param headless: if False, disables the headless mode.
						
    """
    import time

    # Import the OpenOffice Component Context.
    comp_context = uno.getComponentContext()
    
    # Now access the UnoUrlResolver service. This will allow you to connect
    # to OpenOffice.org program.
    resolver = comp_context.ServiceManager.createInstanceWithContext(
        "com.sun.star.bridge.UnoUrlResolver", comp_context)

    cmd = "uno:socket,host=%(server)s,port=%(port)s;urp;StarOffice.ComponentContext" % {
        'server':server,'port':port}

    if not test_srv_connection(server, port, timeout=3) and \
           server in ('127.0.0.1', 'localhost'):
        warnings.warn("Couldn't connect to server: %s:%s - trying to launch it" % (
            server, port), RuntimeWarning, stacklevel=1)
        start_oo(server, port, headless)
        #Wait 3 seconds for openoffice to load.
        time.sleep(3)

    try:
        # Now load the context and you are now connected. You can access OpenOffice
        # via its API mechanism.
        oo_context = resolver.resolve(cmd)

    except NoConnectionException, e:
        # Launching openoffice
        if server not in ('127.0.0.1', 'localhost'):
            warnings.warn("couldn't connect to server: %s:%s" % (server, port),
                         RuntimeWarning, stacklevel=1)
            raise


    return oo_context


class Context(object):
    """
    A context used to render a template. It contains both the data and the way to
    substitute variable with the data.

    """

    translate = None
    """A translation dict. Whenever a variable pattern is found in a
    document, it will be searched for in this dictionary to see if it should
    be translated before sarching in the context.  The goal is to allow
    short variable names in template for narrow cells even if the real
    attribute name in the program is longer. e.g.::

       context.translate['a'] = 'client.user.address'
       context.translate['mq'] = 'minimum_quantity_in_store'

    would allow to write ``$u.city``  instead of ``$client.user.addres.city``
    and ``$mq`` instead of ``$minimum_quantity_in_store``
    """
    def __init__(self, content, lazy=True):
        """
        :param content: a dict with keys the variable names

        :param lazy: boolean. If True (default) invokes
               _implement_lazy_tables to allow the list of objects for a
               table rendered to be directly set as value of the table_name
               entry (rather than a list of lists). See
               :ref:`example` ``Table1`` is lazy ``Table2`` is not.

               The goal is to prevent common errors rather than promoting
               lazy writing. When you only have a single list of objects you
               may easily forget that you may have more than one.

               The assumption is that you don't normally have lists as values
               of context (other that for tables). While probably true, should
               you need lists as contetxt values, you can just set lazy=False.

        """
        self.content= content
        if lazy:
            self._implement_lazy_tables()
        self.translate = {}

    def __getitem__(self, key):
        return self.content[key]
    
    def __setitem__(self, key, value):
        self.content[key] = value
    
    def __contains__(self, key):
        return key in self.content
    def _implement_lazy_tables(self):
        """
        implement a lazy context where lists are directly values of
        contents[Table_name] rather then conten[Table_name] = ((...),)
        """
        for key, value in self.content.iteritems():
            if isinstance(value, (list, tuple)) and len(value):
                if not isinstance(value[0], (list, tuple)):
                    self.content[key] = (value, )
                    
    def sub(self, match=None, key=None):
        """
        Substitution used in normal find & replace on the whole document.
        The match must have a group named 'var_name'
        
        :param match: the match resulting from re.match. if match is None the key
                      is taken from m.group('var_name')
        :param key:   just usefull for debugging purpose. 
        """
        if not key:
            assert match is not None
            key = match.group('var_name')
            
        key = self.translate.get(key, key)
            
        try:
            value = self.content[key] 
            value = unicode(self.value2string(value, key))
            return value
        except KeyError, e:
            return self._deep_sub(None, *key.split('.'))

    def sub_cell(self, match, record_index, table_name, list_num):
        """
        Substitution used for cell values. Specialized version of sub that
        knows how to retrieve data from the object of the cell.

        :param match:         a match that have groups named 'var_name' and 'match'
        :param record_index:  the index of the record in the table's list
        :param table_name:    the openoffice name of the table
        :param list_num:      the odered number of the list in the table (starts from 1).
                              

        """
        assert table_name in self.content, "%s not in context" % self.table_name

        key  = match.group('var_name')
        key = self.translate.get(key, key)
        match =  match.group('match').replace('$', r'\$')
        try:
            ## the object where we get the values are in a list
            obj = self.content[table_name][list_num][record_index]
            value = unicode(self.value2string(getattr(obj, key), key))

            return unicode(match.sub(value))

        except (KeyError, AttributeError), e:
            return self._deep_sub(obj, *key.split('.'))

    def _deep_sub(self, obj, key, *tokens ):
        """
        search a value in nested structure (eg.: user.name, rs.address.city)
        """
        key = self.translate.get(key, key)
        test_split = key.split('.')
        if len(test_split) > 1:
            return self._deep_sub(obj, *(test_split + list(tokens)))
        try:
            if obj:
                value = getattr(obj, key)
            else:
                value = self.content[key]
        except (KeyError, AttributeError), e:
            self.missing_keys[key] = None
            return "Missing Key " + key

        for tk in tokens:
            try:
                value = getattr(value, tk)
            except AttributeError, e:
                self.missing_keys[tk] =  "%s.%s (%s)" % (key, tk, value)
                value = "No attr %s in %s" % (tk, value)

        return unicode(self.value2string(value, key))

    def _get_records_len(self, table_name, list_num):
        """
        return the number of records that must be rendered for this table
        """
        try:
            return len(self.content[table_name][list_num])
        except KeyError:
            print "No TableName %s in context" % table_name
            return 0

    def value2string(self, value, key):
        """
        :param value: the value found in context
        :param key: the key used to retrieve the value. Note that it is ony
            partially usefull as it can be a key of the context or an attribute
            name of an object containted in the context or in a row

        customize the value from the context.
        You are supposed to customize this method that currently only
        trasforms a date in a locale compliant form (if locale is set)
        """
        ## Don't write 'None' for None...
        if value is None:
            return ''

        if isinstance(value, datetime.date):
            return value.strftime('%x')

        return value

    def reset_missing(self):
        """
        reset list of key missing in the context
        """
        self.missing_keys = {}

    def update(self, d):
        """
        Add dict ``d`` to content of this context

        :param d: the dict I want to add to context
        """
        self.content.update(d)

    def __str__(self):
        return "%s" % self.content

class Template():
    """
    The class template that connects to a server (or starts a local one), read a
    document, parses the document to find tables
    """

    DEFAULT_VARIABLE_PATTERN = '(?P<match>\$(?P<var_name>[^ ,\n-\)\t]+))'
    DEFAULT_VARIABLE_PATTERN_OO = '$[^ ,\n\-)\t]+'
    DEFAULT_MULTI_LINE_MARKER = '(?P<match>\+\+)'  # a re.match pattern i.e. starts from beginning of string

    VARIABLE_PATTERN    = None
    """the pattern for python variable detection. it's a regular expression read
    :attr:`set_pattern` for details"""

    VARIABLE_PATTERN_OO = None
    """the pattern for openoffice variable detection. read :attr:`set_pattern` for details """

    MULTI_LINE_MARKER   = None
    """the pattern used to tel when a multiline line starts. Defaults to ++"""

    oo_context = None
    """the connection with the server. This can be reused between templates"""

    document = None
    """the openoffice document from the server"""

    search = None
    """the openoffice SearchDescriptor"""

    preserve_styles = False
    """Preserve style of each word in the cell when cloning rows.
    This will slow down the process so it's disabled by default"""

    def __init__(self, filename, server='127.0.0.1', port=8100, headless=False,
                 oo_context=None, preserve_styles=False):
        """
        only the ``filename`` is needed if the server is local. If we already
        have a template on the same server we can reuse the ``oo_context``


        :params filename: the template filename in the server's filesystem
        :param server: a server name
        :param port:   the port to connect to
        :param headless: if False, disables the headless mode.
        :param oo_context: the openoffice context (not to be confused with
                           ``oootemplate.Context``). The `oo_context`` plays the role of the
                           connection to the server
        :param preserve_styles: use :class:`TemplateWithStyles` to enforce preservation of
                               styles in each word of the cell when duplicating rows
        """
        self.oo_context = oo_context or connect(server, port, headless)
        self.document = self.open_doc(filename, self.oo_context)
        self.cursor = self.document.Text.createTextCursor()
        self.preserve_styles = preserve_styles
        self.tables = self.get_tables()
        self.search = self.document.createSearchDescriptor()
        self.search.SearchRegularExpression = True
        self.search.SearchCaseSensitive = True
        self.search.SearchWords = True

        self.VARIABLE_PATTERN    = re.compile(self.DEFAULT_VARIABLE_PATTERN)
        """the pattern for python variable detection. It's a regular expression,
        read ``set_pattern`` for details"""

        self.VARIABLE_PATTERN_OO = self.DEFAULT_VARIABLE_PATTERN_OO
        """the pattern for openoffice variable detection. read ``set_pattern`` for details """

        self.MULTI_LINE_MARKER   = self.DEFAULT_MULTI_LINE_MARKER
        """the pattern used to tel when a multiline line starts. Defaults to ++"""
        
    def set_pattern(self, pattern, oo_pattern):
        """
        Set the pattern to detect what is a variable to be substituted
        
        :param pattern: the pattern with syntax suitable for module ``re`` module.
             It must define at least 2 groups: ``var_name`` and ``match`` pointing
             respectively to the name of the  variable and the whole match.
             Default is ``(?P<match>\$(?P<var_name>[^ ]+))``

        :param oo_pattern: the pattern with syntax suitable for openoffice regexp search.
             It can only use the openoffice syntax. Default is ``$[^ ]+``
        """
        self.VARIABLE_PATTERN = re.compile(pattern)
        self.VARIABLE_PATTERN_OO = oo_pattern

    def open_doc(self, filename, oo_context):
        """ 
        open the template file and return the document
        
        Se url sbagliato ::

          SystemError: pyuno runtime is not initialized, (the pyuno.bootstrap needs
          to be called before using any uno classes)
          WARNING: Failure executing file: <test.py>
        
        """
        url = self.filename_to_url(filename)
        desktop = oo_context.ServiceManager.createInstanceWithContext(
                "com.sun.star.frame.Desktop", oo_context)

        prop_ro = PropertyValue('ReadOnly', 0, True, 0)
        prop_h  = PropertyValue('Hidden', 0, True, 0)
        try:
            document = desktop.loadComponentFromURL(url, "_blank", 0, (prop_ro, prop_h, ))
        except IllegalArgumentException, e:
            msg = "Original error: '%s'\nTemplate may have a wrong name: %s" % (str(e), filename)
            raise WrongTemplateName(msg)
        
            
        return document

    def filename_to_url(self, filename):
        
        # This will not always work if the server is remote: it depends on the OSs
        # eg.: under windows would become file://C:/... that has no meaning in a *nix server
        #url = uno.systemPathToFileUrl(filename)
        # 
        if not re.search('://', filename):
            url = u'file://%s' % filename
        else:
            url = unicode(filename)
        return url
    
    def get_tables(self):
        """
        returns a table_dict {table_name:table_obj} containing all tables found
        """
        qty = self.document.TextTables.Count
        table_dict = {}

        for n in range(qty):
            oo_table = self.document.TextTables.getByIndex(n)
            table_name = oo_table.getName()

            if self.preserve_styles:
                table = TableWithStyles(oo_table, self)
            else:
                table = Table(oo_table, self)
            table_dict[table_name] = table

        return table_dict

#### Render

    def render(self, context):
        """
        substitute all the variables with values from context

        :param context: the Contex instance to be used
        """
        context.reset_missing()
        self.context = context

        for table_name, table in self.tables.iteritems():
            table.render(context)
            
        self.find_and_replace(context)

        return context.missing_keys
        
    def find_and_replace(self, context, search_obj=None):
        """
        This function searches and replaces. Create search, call function findFirst,
        and finally replace what we found.
        """
        pattern = self.VARIABLE_PATTERN
        (search_obj or self.search).SearchString = self.VARIABLE_PATTERN_OO

        found = self.document.findFirst( self.search )

        while found:
            m = pattern.match(found.String)
            new_text = pattern.sub(context.sub(m), found.String)
            found.String = new_text
            found = self.document.findNext( found.End, self.search)

    def save_as(self, filename, local=None):
        """
        save the template using save_as capability of openoffice.

        :param filename: filename in the `server`'s filesystem. The extension is used to
               detect the file type as in regular openoffice use.
        """
        document = self.document
        
        path, file_ = os.path.split(filename)
        name, extension = os.path.splitext(file_)

        if extension == '.odt':
            url = self.filename_to_url(filename)
            document.storeToURL(url,())
        elif extension == '.pdf':
            url = self.filename_to_url(filename)
            prop = PropertyValue( "FilterName" , 0, "writer_pdf_Export" , 0 )
            document.storeToURL(url, (prop,))
        else:
            filename = filename+'.odt'
            print 'Unsupported Extension "%s", saving as "%s"' % (extension, filename)
            url = self.filename_to_url(filename)
            document.storeAsURL(url,())

    #     if local:
    #         self.save_local(filename, local)

    # def save_local(remote_path, local_path):
    #     """
    #     Retrieve the remote 
    #     """
    def close(self):
        """
        close the related document
        """
        self.document.close(True)
####
class Table():
    """ table object
    detail on the API exposed by uno:
    http://api.openoffice.org/docs/common/ref/com/sun/star/table/module-ix.html
    """
    def __init__(self, oo_table, template):
        """
        :param oo_table: the openoffice table object
        :param template: the ``oootemplate.template`` object in which this table is
        """

        self.table = oo_table
        self.name = oo_table.Name
        self.rows = self.table.getRows()
        self.template = template
        
    def _get_rows_num(self):
        return self.table.Rows.Count

    rows_num    = property(_get_rows_num)

    def __str__(self):
        return "Table Object"

    def add_rows(self, index, count):
        """
        Insert `count` rows just before position `index`

        :param index:  index `before` which rows will be added
        :param count:  number of rows to add
        """
        self.table.Rows.insertByIndex(index, count)

    def del_rows(self, index, count=1):
        """
        Delete count rows just before position index
        """
        self.table.Rows.removeByIndex(index, count)

    def render(self, context):
        """
        render the table with the context

        :param context: the Context object that holds the data 
        """
        list_num = 0
        offset = 0    # increments after rows are added
        for r in range(self.rows_num):
            row_data = self.get_row(r + offset, data_array=True)
            for c, text in enumerate(row_data):
                if re.match(self.template.MULTI_LINE_MARKER, text):
                    ## get rid  of the multiline marker
                    self.set_text(c, r+offset, re.sub(self.template.MULTI_LINE_MARKER, '', text))

                    row_data = self.get_row(r+offset, data_array=True)
                    offset += self._render_rows(r+offset, row_data, context, list_num) 
                    list_num += 1

    def _render_rows(self, r, row_data, context, list_num):
        """
        render the row adding as many rows as needed for the records present in contex
        for this table and using the prototipe in row_data
        """

        n_records = context._get_records_len(self.name, list_num)
        pattern = self.template.VARIABLE_PATTERN
        self.add_rows(r, n_records)

        j = 0
        for j in range(r, r + n_records):
            for k, value in enumerate(row_data):
                ## a cell can have more variables  | $d.first_name $d.last_name | $year |
                def sub(m):
                    return context.sub_cell(m, record_index=j-r, 
                                     table_name=self.name, list_num=list_num)                    

                text = pattern.sub(sub, value)

                self.set_text(k, j, text)

        self.del_rows(j+1) # this row deletes the row with ++$obj...

        return n_records -1 # we added n_records and deleted 1

    def get_row(self, r, data_array=True):
        """
        return the row at position r

        :param r: index of the row to return
        :param data_array: return a tuple of the data instead. If ``False`` an Openoffice
                           ``CellRange`` object is returned
        """
        assert r < self.rows_num, "Max row index for table %s is %s (requested %s)"% (
            self.name, self.rows_num-1, r)
        
        ## I wasn't able to find a way to get the maximum number of columns
        ## table.Rows.Count returns the number of columns of the first row.
        for c in xrange(30):
            try:
                row = self.table.getCellRangeByPosition(0, r, c, r)
            except OutOfBoundsException:
                break
                pass
            
        if data_array:
            return row.DataArray[0]
        else:
            return row
                
    def get_text(self, c, r):
        return self.table.getCellByPosition(c,r).getString()

    def set_text(self, c, r, value):
        self.table.getCellByPosition(c,r).setString(value)

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self.name)

class TableWithStyles(Table):
    """
    A Table that clones rows preserving style info even if several different styles
    are used within the same cell. This process is slower so it's not active by default:
    set Template's arg ``preserve_styles`` to True to enable it (see ex. N. 5).
    
    """
    
    def render(self, context):
        """
        render the table with the context

        :param context: the Context object that holds the data 
        """
        list_num = 0
        offset = 0    # increments after rows are added
        for r in range(self.rows_num):
            row_data = self.get_row(r + offset, data_array=True)
            for c, text in enumerate(row_data):
                if re.match(self.template.MULTI_LINE_MARKER, text):
                    ## get rid  of the multiline marker
                    #self.set_text(c, r+offset,
                    #  re.sub(self.template.MULTI_LINE_MARKER, '', text))
                    self.replace_marker(c, r+offset)

                    row_data = self.get_row(r+offset, data_array=True)
                    offset += self._render_rows(r+offset, row_data, context, list_num) 
                    list_num += 1

    def _render_rows(self, r, row_data, context, list_num):
        """
        render the row adding as many rows as needed for the records present in contex
        for this table and using the prototipe in row_data
        """

        n_records = context._get_records_len(self.name, list_num)
        pattern = self.template.VARIABLE_PATTERN
        self.clone_rows(r, n_records -1)

        j = 0
        for j in range(r, r + n_records):
            for k, value in enumerate(row_data):
                try:
                    self.sub_text_in_cell(k, j, context, record_index=j-r, list_num=list_num)
                except OutOfBoundsException:
                    pass
            
        return n_records -1 # we added n_records -1

    def sub_text_in_cell(self, c, r, context, record_index, list_num):
        # substitution that preserves the style of the caractes
        cell = self.table.getCellByPosition(c,r)
        cursor = cell.createTextCursor()
        ## a cell can have more variables  | $d.first_name $d.last_name | $year |
        while True:
            m = re.search(self.template.VARIABLE_PATTERN,cell.String)
            if not m:
                break
            cursor.gotoStart(False)
            cursor.goRight(m.start('match'), False)
            cursor.goRight(m.end('match') - m.start('match'), True)
            new_text = context.sub_cell(m, record_index=record_index, 
                                        table_name=self.name, list_num=list_num)
            cell.insertString(cursor, new_text, True)

    def replace_marker(self, c, r):

        cell = self.table.getCellByPosition(c,r)
        m = re.search(self.template.MULTI_LINE_MARKER, cell.String)
        if not m:
            return
        cursor = cell.createTextCursor()
        cursor.gotoStart(False)
        cursor.goRight(m.start('match'), False)
        cursor.goRight(m.end('match') - m.start('match'), True)
        cell.insertString(cursor, '', True)

    def clone_rows(self, index, count):
        """
        Insert `count` rows just before position `index`

        :param index:  index 0-based of the row that must be cloned
        :param count:  number of rows to add
        """
        self.table.Rows.insertByIndex(index, count)
        ## Let us fill with the same content
        controller = self.template.document.getCurrentController()
        view_cursor = controller.getViewCursor()
        
        for c in xrange(300):
            try:
                src_cell = self.table.getCellByPosition(c, index + count)
            except OutOfBoundsException:
                break
            view_cursor.gotoRange(src_cell.Text, False)
            transferable = controller.getTransferable()
            
            for j in range(index , index + count ):
                try:
                    dst_cell = self.table.getCellByPosition(c, j)
                except OutOfBoundsException:
                    break
                view_cursor.gotoRange(dst_cell.Text, False)
                controller.insertTransferable(transferable)
                
    def clone_rows_dispatcher(self, index, count):
        """
        Insert `count` rows just before position `index`

        :param index:  index `before` which rows will be added
        :param count:  number of rows to add
        """
        # this would probably be a little faster than the one based on getTransferable()
        # but I can't understand how to copy the Row. It seems that the EntireRow doesn't
        # select any text, whe run from within uno in headless mode
        self.table.Rows.insertByIndex(index, count)
        dispatcher = self.template.oo_context.ServiceManager.createInstance(
             'com.sun.star.frame.DispatchHelper')
        controller = self.template.document.getCurrentController()
        frame = controller.getFrame()

        ## Let us fill with the same content
        src_cell = self.table.getCellByPosition(0, index + count)
        view_cursor = controller.getViewCursor()
        view_cursor.gotoRange(src_cell.Text, False)
            
        dispatcher.executeDispatch(frame, ".uno:EntireRow", "", 0, tuple())
        dispatcher.executeDispatch(frame, ".uno:Copy", "", 0, tuple())

        for j in range(count):
            dst_cell = self.table.getCellByPosition(0, index + j)
            view_cursor.gotoRange(dst_cell.Text, False)
            dispatcher.executeDispatch(frame, ".uno:Paste", "", 0, tuple())
            
#    clone_rows = clone_rows_dispatcher
    



# Cursor.CharWeight = com.sun.star.awt.FontWeight.BOLD
    def __repr__(self):
        return '<TT %s %s>' % (self.__class__.__name__, self.name)

def test_srv_connection(host, port, timeout=3):
    """
    test TCP connectivity
    :param host: the host on which the server must be tested
    :param posrt: the port to test
    :param timeout: timeout for the socket (default 3)
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect((host, int(port)))
        sock.close()
        return True
    except socket.error, err:
        return False

