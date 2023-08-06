# -*- coding: utf-8 -*-
'''
This module provides the ``includesh`` directive. It is implemented by
:class:`IncludeShellDirective` class.
'''
import os
import re
import types
import tempfile

# Import required docutils modules
from sphinx.util.compat import Directive

from docutils import io, nodes, statemachine, utils
from docutils.parsers.rst import directives
from docutils.parsers.rst.directives.misc import Include
# from docutils.parsers.rst.directives.tables import ListTable

import sphinx


#---------------------------------------------------------#
class IncludePyProgramDirective(Include):
  '''
  IncludeShellDirective implements the directive. The class
  is registered as a directive in :func:`rusty.includesh.setup`
  '''
  required_arguments = 1
  optional_arguments = 0
  has_content = None
  node_class = None
  option_spec = {
      'verbatim': directives.flag,
      'docstring': directives.unchanged,
  }

  #---------------------------------------------------------#
  def run(self):
    '''
    Called automatically by the docutils.
    '''

    # Take the current inclusion file, read it and save in
    # temporary location where the actual ``Include`` directive
    # can read it

    # This part is taken from docutils
    if not self.state.document.settings.file_insertion_enabled:
      raise self.warning('"%s" directive disabled.' % self.name)

    source = self.state_machine.input_lines.source(
      self.lineno - self.state_machine.input_offset - 1)

    source_dir = os.path.dirname(os.path.abspath(source))
    path = directives.path(self.arguments[0])

    if path.startswith('<') and path.endswith('>'):
      path = os.path.join(self.standard_include_path, path[1:-1])

    path = os.path.normpath(os.path.join(source_dir, path))
    path = utils.relative_path(None, path)

    try:
      self.state.document.settings.record_dependencies.add(path)
      include_file = open(path, 'r+b')
    except IOError, error:
      raise self.severe('Problems with "%s" directive path:\n%s: %s.'
                        % (self.name, error.__class__.__name__, error))

    try:
      include_text = include_file.read()
    except UnicodeError, error:
      raise self.severe(
        'Problem with "%s" directive:\n%s: %s'
        % (self.name, error.__class__.__name__, error))

    if not 'docstring' in self.options:
      self.options['docstring'] = '__doc__'
      
    self.arguments[0] = self.get_docstring_file(path)

    return Include.run(self)

  def get_docstring_file(self, path):
    p = Program(path)
    tfd, target_path = tempfile.mkstemp(prefix='sd-')
    f = open(target_path, 'wb')
    text = p.docstring
    
    if 'verbatim' in self.options:
      f.write('::\n')
      pat = re.compile('^', re.MULTILINE)
      text = re.sub(pat, "  ", text )      

    f.write("%s\n" % text)
    return target_path


def setup(app):
  '''
  Extension setup, called by Sphinx
  '''
  app.add_config_value('templates_map', {}, 'html')
  # Sphinx 5 support
  if '5' in sphinx.__version__.split('.'):
    app.add_directive('docusage', IncludePyProgramDirective, 0, (0,0,0))
  else:
    app.add_directive('docusage', IncludePyProgramDirective)

class Program(object):

    DOCSTRING = re.compile(
        r'''
        """(?P<docstring>.*?)"""
        ''',
        re.VERBOSE|re.DOTALL
        )
    def __init__(self, filename):

        self.text = open(filename).read()
        self.docstring = self.DOCSTRING.search(self.text).group('docstring')
    
