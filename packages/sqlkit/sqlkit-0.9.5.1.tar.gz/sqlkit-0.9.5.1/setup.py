#!/usr/bin/python

"""GUI to edit databases. Many backend supported (Postgres, Sqlite, MySql,...).
Based on python, GTK, sqlalchemy. It's split into a GUI and a very rich package to create
database interfaces
"""

classifiers = """\
Intended Audience :: Developers
Intended Audience :: Education
Intended Audience :: End Users/Desktop
License :: OSI Approved :: GNU Affero General Public License v3
Operating System :: MacOS
Operating System :: Microsoft
Operating System :: OS Independent
Operating System :: POSIX
Operating System :: POSIX :: Linux
Programming Language :: Python
Topic :: Database :: Front-Ends
Topic :: Software Development :: Libraries
Topic :: Software Development :: Libraries :: Application Frameworks
Topic :: Software Development :: Libraries :: Python Modules"""

import os
import sys
try:
   from setuptools import setup, find_packages
except ImportError, e:
   from distribute_setup import use_setuptools
   use_setuptools()
   from setuptools import setup, find_packages
   
REQUIRES = []

f = open('sqlkit/__init__.py')
for line in f:
   if line.startswith('__version__'):
       version = line.split()[2].strip("'")

if sys.argv[1] == 'install':
   try:
      import pygtk
      pygtk.require('2.0')
   except ImportError:
      print "You need to install also pygtk and I was not able to work out"
      print "  a correct dependency in setup.py"
      sys.exit(1)

# setuptools really fails in understanding which packages are already installed
# pip is much better!
try:
   import sqlalchemy
except ImportError:
   REQUIRES = ['sqlalchemy >= 0.5.4, < 0.7', ]

try:
   import babel
except ImportError:
   REQUIRES += ['Babel']

try:
   import dateutil
except ImportError:
   REQUIRES += ['python-dateutil']

try:
   from sphinx.setup_command import BuildDoc

   class BuildDocFromDir(BuildDoc):
       def run(self):
           """
           Run the normal build but first chdir to the documentation root.
           """
           orig_params = [os.path.realpath( '.' ), self.builder_target_dir, self.doctree_dir]
           os.chdir( self.source_dir )

           self.builder_target_dir = os.path.relpath( self.builder_target_dir, self.source_dir )
           self.doctree_dir = os.path.relpath( self.doctree_dir, self.source_dir )

           BuildDoc.run( self )
           curdir, self.builder_target_dir, self.docree_dir = orig_params
           os.chdir( curdir )
   cmdclass = {'build_sphinx': BuildDocFromDir}

except ImportError:
   cmdclass = {}
   
   
setup(
   name='sqlkit',
   version=version,
   description=__doc__,
   author='Alessandro Dentella',
   author_email='sandro@e-den.it',
   url='http://sqlkit.argolinux.org/',
   install_requires=REQUIRES,
   packages = find_packages('.'),
   classifiers= classifiers.split('\n'),
   include_package_data=True,      
   zip_safe=False,
   cmdclass=cmdclass,
   entry_points = {
      'gui_scripts': [
         'sqledit = sqlkit.scripts.sqledit:main',
         ]
      }
   
   )

