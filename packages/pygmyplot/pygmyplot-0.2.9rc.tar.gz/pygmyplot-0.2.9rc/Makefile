include PackageInfo.cfg
include Makefile.inc

META = $(PACKAGE).__meta__
BUNDLE = $(PACKAGE)-$(RELEASE)
DOCDEST = $(BUILDDIR)/docs
DOCZIP = $(BUNDLE)-docs.zip
DOCPDF = $(PACKAGE).pdf

VERMODULE = $(PACKAGE)/_version.py
INFOFILE = info.py

PRODUCTS = LICENSE.txt $(VERMODULE) $(INFOFILE) $(HTMLDIR)\
                       $(DOCZIP) $(DOCPDF)

all : $(DOCDEST) $(PRODUCTS) sdist

LICENSE.txt : $(INFOFILE)
	$(PYTHON) -c 'exec("import info; \
                            t = open(\"LICENSE.tmplt\").read(); \
                            s = t % vars(info); \
                            open(\"LICENSE.txt\", \"w\").write(s)")'

$(DOCDEST) :
	mkdir -p $(DOCDEST)

$(HTMLDIR) : $(DOCDEST) $(INFOFILE)
	cd $(DOCDIR) ; rm -rf _build/html ; make html
	cp -r $(DOCDIR)/_build/html $(HTMLDIR)
	-rm -f $(DOCDIR)/*.pyc

$(DOCZIP) : $(HTMLDIR)
	-rm -f $(DOCZIP)
	cd $(HTMLDIR) ; zip -ry $(CURDIR)/$(DOCZIP) *
	mv $(DOCZIP) $(DOCDEST)

$(DOCPDF) : $(DOCDEST)
	cd $(DOCDIR) ; rm -rf _build/latex ; make latexpdf
	cp $(DOCDIR)/_build/latex/$(PACKAGE).pdf $(PDFDIR)/$(DOCPDF)
	-rm -f $(DOCDIR)/*.pyc

$(VERMODULE) :
	$(ECHO) '__version__ = "$(RELEASE)"' > $(VERMODULE)

$(INFOFILE) :
	$(ECHO) '# \
	This file is automatically created by make \
	from PackageInfo.cfg\n\
	package = "$(PACKAGE)"\n\
	version = "$(VERSION)"\n\
	release = "$(RELEASE)"\n\
	author = "$(AUTHOR)"\n\
	email = "$(EMAIL)"\n\
	url = "$(URL)"\n\
	copyright = "$(COPYRIGHT)"\n\
	description = "$(DESCRIPTION)"' > $(INFOFILE);

sdist : $(VERMODULE) $(INFOFILE)
	-rm dist/$(BUNDLE).tar.gz
	-rm -f $(PACKAGE)/*.pyc
	$(PYTHON) setup.py sdist
	-rm -f *.pyc

install : all
	$(PYTHON) setup.py install

pypi-upload : all
	$(PYTHON) setup.py sdist upload

clean :
	$(ECHO) Cleaning up in `pwd`.
	-rm -rf $(PRODUCTS)

scrub : clean
	-rm -rf dist/ build/ pygmyplot.egg-info/ *.pyc
