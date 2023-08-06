<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<html xmlns="http://www.w3.org/1999/xhtml">
    <head>
      <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
      ${metatags and metatags or ''}
      <title>${capture(next.show_title)|util.striptags} &mdash; ${docstitle|h}</title>
      ${self.headers()}
<!-- <link rel="stylesheet" href="http://www.myjqueryplugins.com/plugins/jmenu/demo/jquery/jMenu.jquery.css" type="text/css" /> -->
      <link rel="stylesheet" href="${pathto('_static/jMenu.jquery.css', 1)}" type="text/css" />

      <!-- <script type="text/javascript" src="http://www.myjqueryplugins.com/plugins/jmenu/demo/jquery/jMenu.jquery.js"></script> -->

      <script type="text/javascript">

	var _gaq = _gaq || [];
	_gaq.push(['_setAccount', 'UA-18221996-2']);
	_gaq.push(['_trackPageview']);

	(function() {
	  var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
	  ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
	  var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
	})();

      </script>
      <script type="text/javascript" src="${pathto('_static/jMenu.jquery.js', 1)}"></script>
      <script type="text/javascript">
	      $(document).ready(function(){
		      $("#jMenu").jMenu({
			      ulWidth : '150',
			      effects : {
				      effectSpeedOpen : 300,
				      effectSpeedClose : 300,
				      effectTypeOpen : 'slide',
				      effectTypeClose : 'slide',
				      effectOpen : 'linear',
				      effectClose : 'linear'
			      },
			      TimeBeforeOpening : 100,
			      TimeBeforeClosing : 400,
			      animatedText : false,
			      paddingLeft: 1		});
	      })
      </script>
<!-- Preview -->
     <script type="text/javascript" src="${pathto('_static/imgpreview.js',1)}"></script>
     <script type="text/javascript">
       $(document).ready(function(){
           $('.preview').imgPreview();
       });
     </script>
     ${self.extrahead()}
     <!--[if !IE 7]>
	     <style type="text/css">
		     #wrap {display:table;height:100%}
	     </style>
     <![endif]-->
    </head>
    <body>
        ${next.body()}
    </body>
</html>
<%def name="extrahead()"></%def>
##<%def name="body()"></%def>

<%!
    local_script_files = []
%>

