## coding: utf-8
<%inherit file="layout.mako"/>

<%def name="extrahead()">
    <link rel="stylesheet" href="${pathto('_static/tour.css', 1)}" type="text/css" media="screen" />
    <link rel="stylesheet" href="http://apt.argolinux.org/.sk/anythingslider.css" type="text/css" media="screen" />
    <link rel="stylesheet" href="http://apt.argolinux.org/.sk/theme-cs-portfolio.css" type="text/css" media="screen" />
    
    <script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1/jquery.min.js"></script> 
    <script type="text/javascript" src="${pathto('_static/AnythingSlider/js/jquery.easing.1.2.js', 1)}"></script>
    <script type="text/javascript" src="http://apt.argolinux.org/.sk/jquery.anythingslider.min.js"></script>

    <script type="text/javascript">
        function formatText(index, panel) {
		  return index + "";
	    }
    
        $(document).ready(function(){
            $('.anythingSlider').anythingSlider({
	        width : 600,
	        height: 370,
	        theme: 'cs-portfolio',
                delay: 7000,         // How long between slide transitions in AutoPlay mode
	        themeDirectory      : 'css/theme-css-portfolio.css'
##                 easing: "easeInOutExpo",        // Anything other than "linear" or "swing" requires the easing plugin
##                 autoPlay: true,                 // This turns off the entire FUNCTIONALY, not just if it starts running or not.
##                 startStopped: false,            // If autoPlay is on, this can force it to start stopped
##                 animationTime: 600,             // How long the slide transition takes
##                 hashTags: true,                 // Should links change the hashtag in the URL?
##                 buildNavigation: false,          // If true, builds and list of anchor links to link to each slide
##         	pauseOnHover: true,             // If true, and autoPlay is enabled, the show will pause on hover
##         	startText: "",             // Start text
## 		stopText: "",               // Stop text
## 		navigationFormatter: formatText       // Details at the top of the file on this use (advanced use)
             });
        });
    </script>
    
</%def>

<%def name="prevnextheader()"></%def>
<%def name="sidebar()">

  <div class="sphinxsidebar">
     <div class="sphinxsidebarwrapper">
      <div class="news">

      <h2>Release 0.9.5.1 is out</h2>
      
      I'm happy to announce that on Feb, 26 2012 I released 
      <a href="${pathto('misc/download', )}#download">version 0.9.5.1</a> 
      that improves the filter experience and extends support of print also
      using libreoffice beside openoffice.
      (see <a href="/download/Changelog">changelog</a>). 

     </div>

      <div class="news">


     </div>
     </div>

   </div>
</%def>

<div class="promo">
   <div class="box1 box">
      <h1><span style="color: #a91819; font-weight: bold;">Sqledit</span> for end users</h1>

      <b>The easiest possible way to browse the data of your database</b>

      <p>
      You can customize the way data are presented in a very simple way. The
      ideal tool to edit your personal databases or to browse data of an
      application you're developing with other languages/tools.

      <p>
	Filtering data has never been so easy, no SQL knowledge required. 
      <a href="${pathto('misc/sqledit')}">Read more...</a>
      </div>
      <div class="box2 box">
      <h1><span style="color: #a91819; font-weight: bold">Sqlkit</span> for Python developers</h1>

      <b>A powerful framework to create any application from simple
      to very rich and complex ones.</b>
      <p>
	Sqlkit provides 2 widgets to edit data as form or table. It's
	based on PyGTK and sqlalchemy to provide maximum flexibility. 
      <p>
	Key points are the way to design form layout with relationship,
	completions, validation and filter capabilities that can be done w/o
	any effort. More than 80 examples ready to use!
      <a href="${pathto('misc/tour')}">Read more...</a>
   </div>
</div>


<ul class="anythingSlider">
  <li><div class="slider-text">
      <h2>Sqledit</h2>
      <img src="${pathto('_static/images/sqledit_setup.png', 1)}" alt="" />
      The application 'sqledit' can open a great variety of different
      backends as it's base on SqlAlchemy: PostgreSQL, MySQL, sqlite,
      firebird... You can use it to browse your data or to debug an application
      you're developing. The rich configuration capability of sqledit can
      make it grow in a gentle way toward a true application what starts as
      a simple shortcut to some data.
      </div>
  </li>
  <li><div class="slider-text">
      <h2>Table's list</h2>
      <img src="${pathto('_static/images/sqledit.png', 1)}" alt="" />     
      Each table of the database can be opened in Mask or Table way or
      introspected. 
      </div>
  </li>
  <li><div class="slider-text">
      <h2>The model (optional)</h2>
      <img src="${pathto('_static/images/director-model.png', 1)}" alt="" />     
      Table fields can be automatically reflected from the database or set
      using sqlalchemy's standard way. Here the example used in the demo for
      directors and the way to set the relation with 'movie' table.
      </div>
  </li>
  <li><div class="slider-text">
      <h2>Table view</h2>
       <img src="${pathto('_static/images/table.png', 1)}" alt="" />
       Each database table can be opened in table or mask mode. The image 
       shows table mode where each column can be
       sorted and it's field can be added to a filter tool.
      </div>
  </li>
  <li><div class="slider-text">
      <h2>Relationships</h2>
       <img src="${pathto('_static/images/o2m.png', 1)}" alt=""  /><br>
       Create a form to edit relations is as easy as writing a text layout
       (clearly you must define relations in the model):
       <pre>
	 lay = """last_name 
 	          first_name nation
	          o2m=movies"""
	 SqlMask(Movie, layout=lay, dbproxy=db)
      </pre>
      </div>
  </li>
  <li><div class="slider-text">
      <h2>Filters</h2>
       <img src="${pathto('_static/images/filter.png', 1)}" alt="" />
       <p>
       Each field of a table/mask even of a related table can be filtered
       on.  Just click on the label and a filter panel will be presented. A
       smart and efficent way to express dates in a relative way lets you
       great flexibility. Here date_release >= 'y-5' means a film released
       after Jan, 1^ 5 years ago, whenever you run the filter.

      </div>
  </li>
  <li><div class="slider-text">
      <h2>Contraints</h2>
       <img src="${pathto('_static/images/constraints.png', 1)}" alt="" />
       <p>
	 Filters and constraints can be programmatically added using a
	 syntax derived from django orm. User are allowed to play with
	 filters while constraints are used to limit the visibility of some
	 records. 
      </div>
  </li>
  <li><div class="slider-text">
      <h2>Mask View</h2>
       <img src="${pathto('_static/images/ragazza.png', 1)}" alt="" /> 
       
       The SqlMask widget shows one record at a time. Any field type will be
       rendered in a proper way. Images are varchar field for which a
       <tt>render='image'</tt> is set when defining the model. The layout
       can be set in a incredibly simple way w/o any programming knowledge.
      </div>
  </li>
  <li><div class="slider-text">
      <h2>Mask view from any row</h2>
      
       <img src="${pathto('_static/images/rim.png', 1)}" alt="" />
       <p>
       Right click on a record offers a variety of different actions. The most
       important is the ability to open a SqlMask to view/edit that record
       the record pointed to by the foreign key.
      </pre>
      </div>
  <li><div class="slider-text">
      <h2>Registered layout</h2>
       <img src="${pathto('_static/images/rim-bi.png', 1)}" alt="" />
       <p>
	 A mask that displays a single record can use a registered layout
	 and will follow the selection of the underneath table.
      </pre>
      </div>
  </li>
  <li><div class="slider-text">
      <h2>Completion</h2>      
      <img src="${pathto('_static/images/completion.png', 1)}" alt="" /> 
      Any foreign key is automatically detected and a widget that implements
      completion on the foreign table is used. Completion is triggered by
      'Return' and the search on the foreign key is done in a customizable
      field and represented in a customizable way (here: first_name + last_name)
      </div>
  </li>
  <li><div class="slider-text">
      <h2>Group by on completion</h2>
      <img src="${pathto('_static/images/completion_group_by.png', 1)}" 
	   align="right" class="align-right" alt="" /> 
      Completion can be programmed in a group-by fasion or constrained in a
      dinamic way so that the value of a field is used to filter the
      possible completions:
      <br clear="all">
      <pre>
	t = SqlTable(Invoice, ...)
	t.completions.project_id.filter(client_id='$client_id') # dynamic
	t.completions.client_id.group_by = 'category' # group-by
      </pre>

      </div>
  </li>
  <li><div class="slider-text">
      <h2>Totals</h2>
      <img src="${pathto('_static/images/totals.png', 1)}" alt="" /> 
      Table can display totals and subtotals. Here subtotals w/o totals
      where requested.
      </div>
  </li>
  <li><div class="slider-text">
      <h2>Trees</h2>
      <img src="${pathto('_static/images/tree-table.png', 1)}" alt="" /> 
      <p>
      Rows can be displayed with a hierarchy
      </div>
  </li>
  <li><div class="slider-text">
      <h2>Editing joins</h2>
      <img src="${pathto('_static/images/join.png', 1)}" alt="" /> 
      <p>
	Tables and Masks can show any selectable that you may define with
	sqlalchemy. Here a join between two columns is displayed and fields
	from both tables retain the possibility to be edited.
	<pre>
         m = mapper(Join, model.Movie.__table__.join(model.Director.__table__),
           properties={
                 'movie_id' : model.Movie.__table__.c.id
            })
         t = SqlTable(m, dbproxy=db )

        </pre>
      </div>
  </li>
  <li><div class="slider-text">
      <h2>Computed fields</h2>
      <img src="${pathto('_static/images/add_fields.png', 1)}" alt="" /> 
      <p>
	You can add computed fields as in this case where the number of
	movie is computed for each director, you can further sum and sort
	on those fields.
      </div>
  </li>
  <li><div class="slider-text">
      <h2>Printing</h2>
      <img src="${pathto('_static/images/printing.png', 1)}" alt="" /> 
      <p>
	Sqlkit provides a very powerful template system that allows to
	compose the layout with OpenOffice.org. No programming know-how is
	required to create an effective template, no more headache to get
	the right layout using OpenOffice's <tt>writer</tt>.
      </div>
  </li>
  <li><div class="slider-text">
      <h2>HOOKS & signals</h2>
      <p>
      Many signals and hooks are available to the programmer for a powerful
      level of customization. 
      <p>
      A "hook" class can be registered globally so
      that its attached to any SqlWidget open in any situation, both in form
      or table view. That's the "controller" part in the MVC implementation.
      <p>
      Hooks allow you to customize almost any part as are called on
      validation, on completion, on record display, on value change so that
      it's very easy to create a very interactive interface.
      </div>
  </li>
</ul>
