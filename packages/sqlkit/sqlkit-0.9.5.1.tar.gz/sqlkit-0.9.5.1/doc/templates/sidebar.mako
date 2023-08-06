## coding: utf-8
<%inherit file="layout.mako"/>

<p class="logo"><a href="contents.html">
   <img class="logo" src="${pathto('_static/reteisi.css', 1)} alt="Logo"/>
      </a>
</p>

<h3>Navigazione</h3>
        <div class="topnav">
            <div class="navbanner">
                <a class="totoc" href="${pathto(master_doc)}">Table of Contents</a>
                % if parents:
                    % for parent in parents:
                        » <a href="${parent['link']|h}" title="${parent['title']}">${parent['title']}</a>
                    % endfor
                % endif
                % if current_page_name != master_doc:
                » ${parent.show_title()} 
                % endif
                
                ${self.prevnext()}
                <h2>
                    ${self.show_title()} 
                </h2>
            </div>
            % if display_toc and not current_page_name.startswith('index'):
                ${toc}
            % endif
            <div class="clearboth"></div>
        </div>
        


<h3>Download</h3>

    ReteIsi offre una distribuzione live scaricabile dal sito di  
    <a href="http://download.argolinux.org/isi/">Argolinux</a>

    L'ultima versione è la 
    <a href="http://download.argolinux.org/isi/newisi-libata-beta6.iso">
    newisi-libata-beta6</a> basata su etch.

<h3>Domande? Problemi?</h3>

<p>Iscriviti al <a href="http://groups.google.com/group/reteisi">
   Google group</a>:</p>

<form action="http://groups.google.com/group/reteisi/boxsubscribe" style="padding-left: 1em">
  <input type="text" name="email" value="your@email"/>
  <input type="submit" name="sub" value="Subscribe" />
</form>
<div id="searchbox" style="display: none">

<h3>Ricerca veloce</h3>
    <form class="search" action="search.html" method="get">
      <input type="text" name="q" size="18" />
      <input type="submit" value="Vai" />
      <input type="hidden" name="check_keywords" value="yes" />

      <input type="hidden" name="area" value="default" />
    </form>
    <p class="searchtip" style="font-size: 90%">
    Inserisci un termine di ricerca un modulo, classe o nome di funzione
    </p>
</div>
<script type="text/javascript">$('#searchbox').show(0);</script>

