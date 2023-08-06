## coding: utf-8
##<%inherit file="${context['mako_layout']}"/>
<%inherit file="static_base.mako"/>

<%def name="headers()">
    <link rel="stylesheet" href="${pathto('_static/pygments.css', 1)}" type="text/css" />
    <link rel="stylesheet" href="${pathto('_static/sqlkit.css', 1)}" type="text/css" />
    <link rel="stylesheet" href="${pathto('_static/print.css', 1)}" type="text/css" media="print" />

    % if hasdoc('about'):
        <link rel="author" title="${_('About these documents')}" href="${pathto('about')}" />
    % endif
    <link rel="index" title="${_('Index')}" href="${pathto('genindex')}" />
    <link rel="search" title="${_('Search')}" href="${pathto('search')}" />
##    % if hasdoc('copyright'):
##        <link rel="copyright" title="${_('Copyright')}" href="${pathto('copyright')}" />
##    % endif
    <link rel="top" title="${docstitle|h}" href="${pathto('index')}" />
    % if parents:
        <link rel="up" title="${parents[-1]['title']|util.striptags}" href="${parents[-1]['link']|h}" />
    % endif
    % if nexttopic:
        <link rel="next" title="${nexttopic['title']|util.striptags}" href="${nexttopic['link']|h}" />
    % endif
    % if prevtopic:
        <link rel="prev" title="${prevtopic['title']|util.striptags}" href="${prevtopic['link']|h}" />
    % endif
    <script type="text/javascript">
      var DOCUMENTATION_OPTIONS = {
          URL_ROOT:    '${pathto("", 1)}',
          VERSION:     '${release|h}',
          COLLAPSE_MODINDEX: false,
          FILE_SUFFIX: '${file_suffix}'
      };
    </script>
    % for scriptfile in script_files + self.attr.local_script_files: ## jquery.js, doctools.js
    <script type="text/javascript" src="${pathto(scriptfile, 1)}"></script>
    % endfor

</%def>


<div id="wrap">
    ${self.testata()}
    ${self.related()}
    ${self.sidebar()}
    <div class="document">
      <div class="documentwrapper">
        <div class="bodywrapper">

            <div class="body">
                ${next.body()}
            </div>
        </div>
     </div>
   </div>

        <%def name="footer()">
            <div class="bottomnav footer">
                <div class="doc_copyright">
                Alessandro Dentella -- Copyright 2006-2007-2008-2009-2010
		  Sqlkit release ${release}
<!--                 % if hasdoc('copyright'): -->
<!--                     &copy; <a href="${pathto('copyright')}">Copyright</a> ${copyright|h}. -->
<!--                 % else: -->
<!--                     &copy; Copyright ${copyright|h}. -->
<!--                 % endif -->
                % if show_sphinx:
                    creato usando  <a href="http://sphinx.pocoo.org/">Sphinx</a> ${sphinx_version|h}.
                % endif
                </div>
            </div>
        </%def>
</div> <!-- wrap -->
${self.footer()}

<%def name="prevnext()">
<div class="prevnext">
    % if prevtopic:
        Previous:
        <a href="${prevtopic['link']|h}" title="${_('previous chapter')}">${prevtopic['title']}</a>
    % endif
    % if nexttopic:
        Next:
        <a href="${nexttopic['link']|h}" title="${_('next chapter')}">${nexttopic['title']}</a>
    % endif
</div>
</%def>

<%def name="prevnextheader()">
<!-- <div class="prevnext"> -->
<!--    <li class="right"  style="margin-right: 10px">Indice -->
<!--      <a href="${pathto('genindex')}" title="Indice generale" -->
<!--                accesskey="I">indice</a></li> -->

    % if prevtopic:
        <li class="right">Prev:
        <a href="${prevtopic['link']|h}" title="${_('previous chapter')}">${prevtopic['title']}</a></li>
    % endif
    % if nexttopic:
        <li class="right">Next:
        <a href="${nexttopic['link']|h}" title="${_('next chapter')}">${nexttopic['title']}</a></li>
    % endif
<!-- </div> -->
</%def>

<%def name="show_title()">
% if title:
    ${title}
% endif
</%def>

<%def name="sidebar()">
  <div class="sphinxsidebar">
     <div class="sphinxsidebarwrapper">
##	<%include file="sidebar.mako"/>


	    <div class="topnav">
		% if display_toc and not current_page_name.startswith('index'):
    <h3>Table of contents</h3>
		    ${toc}
		% endif
		<div class="clearboth"></div>
	    </div>



    <h3>Questions?</h3>

    <p>Subscribe to out mailing list <a href="http://groups.google.com/group/sqlkit">
       Google group</a>:</p>

    <form action="http://groups.google.com/group/sqlkit/boxsubscribe" style="padding-left: 1em">
      <input type="text" name="email" value="your@email"/>
      <input type="submit" name="sub" value="Subscribe" />
    </form>
    <div id="searchbox" style="display: none">

    <h3>Quick search</h3>
	<form class="search" action="${pathto('search.html', 1)}" method="get">
	  <input type="text" name="q" size="18" />
	  <input type="submit" value="Search" />
	  <input type="hidden" name="check_keywords" value="yes" />

	  <input type="hidden" name="area" value="default" />
	</form>
	<p class="searchtip" style="font-size: 90%">
        Enter search terms or a module, class or function name.
	</p>
    <h3>License</h3>
	<img src="${pathto('_static/gplv3.png', 1)}" alt="logo GPLv3">

    </div>
    <script type="text/javascript">$('#searchbox').show(0);</script>

     </div>
  </div>
</%def>

<%def name="related()">
    <div class="related">
      <ul>
	${self.prevnextheader()}

      </ul>

    </div>
</%def>

<%def name="testata()">
<div id="header">

	<div class="logo"><a href="${pathto('misc/tour')}">
       <img src="${pathto('_static/sqlkit.png', 1)}" align="left"  alt="Logo" border="0"/></a>
        </div>
	<div id="description">Acces to db made easy</div>
</div>


   <div style="clear:left;"></div>


<div >
	<ul id="jMenu">
            <li><a class="fNiv" href="${pathto('index.html', 1)}" title="Home" 
                  >Home</a></li>

            <li><a li class="fNiv" href="${pathto('sqlkit/contents')}"
                  title="Sqlkit - the python package" 
                  >Sqlkit</a>

	       <ul>
		 <li ><a href="${pathto('sqlkit/contents')}"
		       title="Sqlkit - the python package" 
		       >Sqlkit</a></li>

		 <li ><a href="${pathto('sqlkit/sqlwidget')}" title="Widgets" 
		       >Widgets</a>
		       <ul> 
			 <li ><a href="${pathto('sqlkit/mask')}" title="Mask" 
			       >Mask view</a></li>
			 <li ><a href="${pathto('sqlkit/table')}" title="Table" 
			       >Table view</a></li>
		       </ul>
                 </li>
		 <li ><a href="${pathto('sqlkit/browsing')}" title="Browsing Data" 
		       >Browsing data</a>
		    <ul> 
		      <li ><a href="${pathto('sqlkit/constraints')}" title="Constraints" 
			    >Constraints</a></li>
		      <li ><a href="${pathto('sqlkit/filters')}" title="Filters" 
			    >Filters</a></li>
		      <li ><a href="${pathto('sqlkit/totals')}" title="Totals" 
			    >Totals</a></li>
		    </ul>
                 </li>
		 <li ><a href="${pathto('sqlkit/editing')}" title="Editing Data" 
		       >Editing data</a>
			 <ul> 
			   <li ><a href="${pathto('sqlkit/completion')}" title="Completion" 
				 >Completion</a></li>
			   <li ><a href="${pathto('sqlkit/validation')}" title="Validation" 
				 >Validation</a></li>
			   <li ><a href="${pathto('sqlkit/relationship')}" title="Relationships" 
				 >Relationships</a></li>
			 </ul>
		       </li>
		 <li ><a href="${pathto('sqlkit/printing')}" title="Printing" 
		       ><span>Printing</span></a></li>
		 <li ><a href="${pathto('sqlkit/advanced/contents')}" title="Advanced configuration" 
		       >Advanced configuration</a>
			 <ul> 
			   <li ><a href="${pathto('sqlkit/advanced/fields')}" title="Fields" 
				 >Fields</a></li>
			   <li ><a href="${pathto('sqlkit/advanced/views')}" title="Views" 
				 >Views</a></li>
			 </ul>
		       </li>

	       </ul>
            </li>

            <li><a class="fNiv" href="${pathto('misc/sqledit')}"
                  title="Sqledit GUI" 
                  >Sqledit GUI</a></li>

            <li><a class="fNiv" href="${pathto('misc/tutorials')}"
                  title="Support & tutorials" 
                  >Support & Tutorials</a>
	       <ul>
		 <li ><a href="${pathto('misc/sqledit')}"
		       title="Sqledit - the application" 
		       >Sqledit - the application</a></li>
		 <li ><a href="${pathto('misc/tour')}"
		       title="Sqlkit - the features'tour"
		       >Sqlkit - features' tour</a></li>
		 <li ><a href="${pathto('misc/sqledit')}"
		       title="Sqledit - the application" 
		       >Installing instructions</a></li>
		</ul> 
            </li>

            <li><a class="fNiv" href="${pathto('layout/contents')}" title="Layout"
                  >Layout</a></li>

            <li><a  class="fNiv"href="${pathto('misc/contents')}" title="Download" 
                  >Download</a>

	       <ul>
		 <li ><a href="${pathto('misc/contents')}"
		       title="Download"
		       >Download</a></li>
		 <li ><a href="http://sqlkit.argolinux.org/download/Changelog"  title="Changelog"
		       title="Changelog"
		       >Changelog</a></li>
		 <li ><a href="${pathto('misc/backward_incompatibilities')}"
		       title="Backward incompatibilities"
		       >Backward incompatibilities</a></li>
	       </ul>
            </li>



        </ul>
</div>
   <div style="clear:left;"></div>
</%def>
<br style="clear: left" />
