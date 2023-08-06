.. _layout:

=====================================
A GUI description language - purpose
=====================================
 
.. sidebar:: Note

   this page needs to be reviewed. While it should be mostly correct
   when ported to rest format has not been reviewed.
   
   A complete tour of what can be done is available in the demo


The class Layout is a class that understands a GUI description
language to create GUI on the fly, with minimal effort by the programmers,
that doesn't need to know a lot of Gtk details.

You cannot do *any* possible thing you would do with gtk, but methods are
provided to refine the layout and it isn't difficult to add GtkObjects or
features.

The purpose is to easy things with simple setup, not to cover any possible
graphical layout. The main purpose is to be used in designing layout of
record editor (:ref:`sqlkit`) for db, but it can be used with any other
program as well.

Layout is not an interactive tool: it uses gtk.Builder xml to create the GUI, ie:
it produces xml for gtk.Builder.

.. note:: gtk.Builder

   up to 0.9.2 sqlkit used glade. This dependancy has been dropped in favor
   of gtk.Builder that is directly available in standard GTK installation.

Care must be used to create names for the elements that are unique in
the single layout, so as to be able to reach any single object, not only to
refine configuration but also to interact with the GtkObj in the
program. This reflects in the fact that the name is unique.

A normal GUI is plenty of labels and tooltip. 
At the moment of this writing no localization is provided but gettext
support is in program. 

============================
Description of the language
============================

a starting example::
    
    layout = """ 
       el=first_name  el=last_name
       el=address     -
    """
    

A layout is a sequence of tokens and display modifiers.

:token:
  describes a GtkObject (Button, Entry...), may also be a compound. An
  example: el=first_name. They will normally start with a description key,
  followed by a '=' and then followed by a string possibly separated by a
  '/' and.or a::
  
     key=string/variable:wid1.wid2
  
  or in regexp notation and more precise::
  
    (key=)string(.[0-9a-z])?(/variable)((:width.)(width)([-<>]))?
     key   txt    id          var        width1   width2  align
  
  
  no element is needed apart the 'string', the key defaults to 'el' (Entry +
  Label), the variable defaults to the string, wid1 and wid2 (described
  below) use GtkWidget defaults. 
  
  The string part may end with .[a-z0-9] just to be able to refer in a
  unique way to single elements that are apparently equal (see :ref:`names`)

  an indication of the desidered alignment may be given using one of ('-',
  '<', '>'). this take effect oly if the element is position in a
  gtk.Alignment (eg. 'ae' element ie: entry with width). in that case:

    :>: right alignment   (xalign = 1)
    :<: left alignment    (xalign = 0)
    :-: xscale of the alignment is set to 1 i.e. the child of the
        alignment (the entry in the example will grow when more space
	is given to the widget)
	
.. sidebar:: Automatisms with sqlkit

   Note that when used from within sqlkit layout definition any text
   field is rendered with entry within an alignment (``ae`` element) and an
   alignment of '-' is added to any text field longer than 20 chars.

    
:spare token:
  A token may further be:
 
    :@:
      it is equivalent to a newline (in fact I figure it like spinning ;-)
    :-:
      forces the previous element to span one more column to the left
    :^:
      forces the element above it to span one more row down
    :%.*: the element is a label for a notebook (see 'notebook' method)

    
:display modifiers:
  A modifier is an element that modifies the way elements are arranged,
  mainly it modifies the packing info or the container, but can also modify
  the display eg: label and entry on the same line or one above the other.
  A modifier is:
    
    :{}:
      a pair of curly braces
    
    :[XTHVbNPSvhpOBmMFA](.id):
    
       (possibly) followed (w/out spaces) by some opts as in 
       {V r=man/sex r=woman}, this will create a nester layout with 2
       radiobutton packed into a GtkVBox. For an explanation of the (.id)
       part see below (container naming)
       
    
       Possible opts are XTHVbNPSvhpOBmMFA:
    
         :T: gtkTable
         :H: gtkHBox
         :V: gtkVBox
         :N: gtkNotebook
         :F: gtkFrame	
         :M: gtkMenubar
         :t: gtkToolBar
         :h: gtkHPaned
         :v: gtkVPaned
         :S: gtkScrolledWindow
         :B: gtkMenuBar
         :M: gtkMenu
         :m: gtkMenuItem
         :O: gtkToolbar
         :W: Window
         :E: EventBox
         :X: Expander
         :p: ViewPort
         :A: Alignment
          
    

  Elements will be packed in a table widget unless changed by a option
  when instantiating the class as in::

     lay = Layout(lay, opts="V=")

  Other values for opts are ``[>=-|]`` - to be confirmed
     :=:
       implies that label and entry will be displayed one over the other (this
       is the default)
     :-:
       implies that label and entry will be displayed on the same line.
     :\|: 
       will draw a line around the widgets, using a frame. That means a GtkFrame
       and a GtkAlignment are silently created. You can set
       properties of the silently created expander using key F.id
     :>: 
       will encapsulate the result into an Expander that allows to
       collapse all its content via a click on a little arrow. You can set
       properties of the silently created expander using key X.id. A double
       '>>' results in an expanded expander. The id is used as label for the
       expander. so that '>>.clients', will be expanded in an oped expander
       with a label "clients"
  

       
a longer example
----------------

::

   el=first_name                  el=last_name
   el=address                     -
   {V r=man/sex      r=woman/sex}  b=register







Comment
--------

A '#' sign starts a comment. Anything till the end of the line will be
discarded, as usual...



el element
-----------

the most used element will probably turn out to be a Label + Entry widget
that can be constructed as in el=first name. It will really be understood
as::

    { l=first_name el=first_name }

or::

  { l=first_name 
    el=first_name }

According to the opt modifier = or - 




list of elements
================

A partial list of elements:

    :l: Label,
    :L: EventLabel, a label in a GtkEventBox
    :e: Entry,
    :E: Event,
    :b: Button,
    :r: RadioButton,
    :c: CheckButton,
    :TV: TreeView,
    :TX: TextView,
    :TVS: ScrolledTreeView,
    :TXS: ScrolledTextView,
    :cal: Calendar,
    :sb: Statusbar,
    :le: ComboLE,

    more symbols are in the source...



custom  widgets
---------------

Occasionally you will find yourself in nee for a custom identifier. You can
create one and register it. Have a look at the code in layoutgenerator
module.


Calling Layout
==============

::

    def __init__(self, lay, level=0, parent_container="W", opts="T",
                 elements={}, container_id='',title="Window",dbg=0):

:lay:
  the string describing the desired layout
:level: 
  nested level (used only by layout itself)
:parent_container:
  a flag among the container flags that says which is the container: determines
  the packing info for the result. Default is W (Window) as a toplevel
  window. In this case info for a toplevel window is built.
:opts:
  This string has the same meaning of the modifier string of a container that
  can be put directly after the '{' char.

  Mainly this is a way to force the use of a container for the outer call of
  layout. Default is to put all widgets in a GtkTable but any container can be
  chosen from the container flags.
  
  A special component of 'opts', is 's' that asks to add a StatusBar. The
  method 'sb' is provided to talk with that Statusbar whose key name is sb=StBar.
  
:addto:
  follows the name of a container that will receive the resulting
  layout. Must be a container that accept 'add' method.







methods
--------


NOTE: some methods can only be called after 'show' has being called. These
methods use gtk directly, not glade.


   :xml(file=None): 
             will produce the xml needed for glade, may be write to file

   :show(action=function_name): will directly call glade to display the
             GUI, returns a dict of Gtk objects whose keys are the element
             *keys*. After this method there is no point in changing
             elements[] properties. The action can be gtk.main.
	     
   :elements: a dict of all lwidgets. The keys are the element
     definitions. Any element can be configure up to the moment show is called.

   :conf(el,property): 
     will set a property for an element of the layout  equivalent to::

           elements['el_key'].properties['name'] = value

   :sig(list): 
     will set handlers for the signal for each widget. The list
     is a list of tuples of 3 elements:
     
        * el_key 
	* handler 
	* signal. If the last is missing, clicked is used

   :tip (el, text): 
         a tooltip for the element 'el'. It tip is called before 
         'show', it will end up in xml+glade, otherwise it will call 
	 gtkTooltip directly

   :sb(text): 
        will push text on the StatusBar

   :menu('el_key', (entry-name, handler, signal=activated), 'i'), (), ():
        Will add MenuItems (Stock ImageMenuItems if 4^ element is 'i')

   :notebook('el_key', ['label 1', 'label2',...],position):
        Adds the label to tabs and allow to set the position (top,left,
        right, bottom) for a GtkNotebook. There is another way to obtain
        this effect. You can add %label as first entry in the block that
        will be enclosed in the notebook. See below: notebook

   :frame('el_key', 'label'):
        Adds a label to a frame, and writes it w/ bold face

   :prop(el_key,property_name, value):
        Sets a property  for element el_key

   :pack(el_key,property_name, value):
        Sets a pack property for element el_key

.. _names:

element names
=============

For each element of the layout we need to build a key for xml, so that we
know how to refer to the gtk object in the program. Layout will build the
name starting from what was written in the element description, if that
results in being already used it builds a unique name adding a number, but that 
may result in difficulty to interact with it from inside the program.

If that's an issue try being clear when creating the layout. Use ids, the
string separated by a '.' that you can add to element names and to container
flags:

  :container:
    ::

      {H.Z   {B.id0

  :element names:
    ::

       e=name.id1/string


stock names
--------------

if the name of an element starts with 'gtk-', use-stock = True is set for
that element.

Notebook
--------


A notebook need some labels to identify the tabs. These are other child of
the GtkNotebook container interspersed with the content of the
container. You can set them with the notebook method, or you can use a
symbol in the describing string using % trailer:: 

  
  {N.0  { %first_tab_RIGHT
        TXS=one }
      { %second_tab
        TXS=due
      }
  }


will be equivalent to::

   l.notepad('N.0', ['first tab','second tab'], 'right')

Please, note that you can enforce a position with a trailing _(LEFT|TOP|...)
to the first label. Note also that any underscore will be substituted w/ a
space.  



Automatic name mechanism
----------------------------


A normal element definition is of the form::

    key=string/variable:width.height


  * the :width.width part is discarded
  * the rest is used as key, *but*
  * if no 'key=' part was explicitly used as in 'first_name' two will be
    created: e=string, l=string



container naming
------------------

Containers need a name too. You are supposed to know which one is used: it
will be GtkTable unless you asked for a different one. You need it in case
you want to modify its properties.

Their name will be the container flag [THVbNPSvhpOBmMFA] possibly followed
by a dot . and an identifier. The identifier will be a progressive counter,
starting from 0 but may be imposed appending .id to the flags of the
container, as in::

  {V.my_id first_name last_name }



Functions
=========

``map_layouts(filename=None, buf=None)``

This functions fills in a dictionary widgets.info whose structure is:

  name : (label, tip)

when a widget is created w/ name 'name' the label will be set to 'label' and
a tooltip will be set to 'tip'. This can help a lot in many situations. Db
field name will be mapped to user friendly labels, translation will be as
easy as pointing to a different file. 

The function can point to a filename or can read a string. You can write
directly the info dictionary if you prefer...



Layout class implementation
===========================


Each layout live in a container (may be a toplevel Window) and creates a
container to house its children. This can cause a little bit of
confusion so I call parent_container the container in which a widget live and
container the Gtk container (Table, HBox, VBox...) where I house layout children.

You can think at your layout as divided in blocks, each one named 'cell' in
the code. A cell is or the definition of a gtkObj or a nested layout.
You can see this list for debugging purposes with method _dbg_parse_layout.

You can think at these cells as displayed in a grid, each one defined by a
row and a column. The constructor of Layout uses a dict named 'cells' with
indices (row,col) to store the name of the corresponding LWidget or
LContainer.

When the object is instantiated, Layout

  1. creates a container (LContainer object)
  2. splits the layout description into tokens that are or 
     -a element descriptions 
     - nested layouts (starts w/ '{')
     ...

For each token that describes a single element, creates the corresponding
lwidget object, for each nested layout creates another instance of Layout.

LWidgets and LContainer
-------------------------

the difference between an LWidget and an LContainer is that an LContainer has
children and must pack info for all the children when producing xml (apart
from producing the xml for itself)

Window creation
----------------


Each call to Layout must create a container to house all its children, but
the first (or outer) one needs normally to create also the TopLevel Window,
that to us is nothing than another LContainer whose (only) child is just
another container (the outer one for Layout).


Producing xml
-------------

Layout produces xml just asking to the toplevel (an LContainer object) to
produce xml.  LContainer xml, produces xml for itself and for its children,
if some of them is a container the process iterates.
