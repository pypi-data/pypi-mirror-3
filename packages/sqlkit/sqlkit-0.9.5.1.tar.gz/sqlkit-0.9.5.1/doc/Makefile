# Makefile for Sphinx documentation
#
VER           = 0.9.5
DEBVER        = 0.8.6.1-1
WINVER        = 0.8.6.1
LNXVER        = 0.9-rc1

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
PAPER         =

# Internal variables.
PAPEROPT_a4     = -D latex_paper_size=a4
PAPEROPT_letter = -D latex_paper_size=letter
ALLSPHINXOPTS   = -d .build/doctrees $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) .

.PHONY: help clean html web pickle htmlhelp latex changes linkcheck
all:    html
help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  html      to make standalone HTML files"
	@echo "  pickle    to make pickle files (usable by e.g. sphinx-web)"
	@echo "  htmlhelp  to make HTML files and a HTML help project"
	@echo "  latex     to make LaTeX files, you can set PAPER=a4 or PAPER=letter"
	@echo "  changes   to make an overview over all changed/added/deprecated items"
	@echo "  linkcheck to check all external links for integrity"

clean:
	-rm -rf .build/*

html:
	mkdir -p .build/html .build/doctrees
	$(SPHINXBUILD) -b html $(ALLSPHINXOPTS) .build/html
	@echo
	@echo "Build finished. The HTML pages are in .build/html."
	@perl -i -p -e 's/DEBVER/$(DEBVER)/g' .build/html/misc/download.html
	@perl -i -p -e 's/WINVER/$(WINVER)/g' .build/html/misc/download.html
	@perl -i -p -e 's/LNXVER/$(LNXVER)/g' .build/html/misc/download.html
	@perl -i -p -e 's/VER/$(VER)/g' .build/html/misc/download.html
	@perl -i -p -e 's/VER/$(VER)/g' .build/html/misc/tutorial.html

pickle:
	mkdir -p .build/pickle .build/doctrees
	$(SPHINXBUILD) -b pickle $(ALLSPHINXOPTS) .build/pickle
	@echo
	@echo "Build finished; now you can process the pickle files or run"
	@echo "  sphinx-web .build/pickle"
	@echo "to start the sphinx-web server."

web: pickle

htmlhelp:
	mkdir -p .build/htmlhelp .build/doctrees
	$(SPHINXBUILD) -b htmlhelp $(ALLSPHINXOPTS) .build/htmlhelp
	@echo
	@echo "Build finished; now you can run HTML Help Workshop with the" \
	      ".hhp project file in .build/htmlhelp."

latex:
	mkdir -p .build/latex .build/doctrees
	$(SPHINXBUILD) -b latex $(ALLSPHINXOPTS) .build/latex
	@echo
	@echo "Build finished; the LaTeX files are in .build/latex."
	@echo "Run \`make all-pdf' or \`make all-ps' in that directory to" \
	      "run these through (pdf)latex."

changes:
	mkdir -p .build/changes .build/doctrees
	$(SPHINXBUILD) -b changes $(ALLSPHINXOPTS) .build/changes
	@echo
	@echo "The overview file is in .build/changes."

linkcheck:
	mkdir -p .build/linkcheck .build/doctrees
	$(SPHINXBUILD) -b linkcheck $(ALLSPHINXOPTS) .build/linkcheck
	@echo
	@echo "Link check complete; look for any errors in the above output " \
	      "or in .build/linkcheck/output.txt."

rsync:	html
	rsync -r --delete --progress --stats .build/html/ www3:docs/sqlkit/

pdf:    latex
	cd .build/latex; make all-pdf
	Print -s -o "-b 20" .build/latex/sqlkit.pdf
	gv --orientation=seascape .build/latex/sqlkit.2.ps


galeon: 
	galeon .build/html/index.html

firefox: 
	firefox .build/html/index.html

chtml:	clean html

refs:
	find -name \*rst -exec grep -oE '\.\. \_([^:]+):\s*' {} \; 	
css:
	cp static/*css ./.build/html/_static/
	cp ./static/AnythingSlider/css/page.css ./.build/html/_static/AnythingSlider

refresh:
	touch misc/tour.rst misc/download.rst misc/sqledit.rst
	make
