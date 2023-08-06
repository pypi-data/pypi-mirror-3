#------------------------------------------------------------------------------
# file: $Id: Makefile 34 2012-07-03 02:48:00Z griff1n $
# desc: pysyncml Makefile
# auth: griffin <griffin@uberdev.org>
# date: 2012/06/30
# copy: (C) CopyLoose 2012 UberDev <hardcore@uberdev.org>, No Rights Reserved.
#------------------------------------------------------------------------------

# PYVER          := $(shell python -V 2>&1)

NOSE            = nosetests
SPHINX          = sphinx-build
RSYNC           = rsync
RSYNCUSER       = griff1n
PY26            = . ~/virtualenv/pysyncml-2.6/bin/activate
PY27            = . ~/virtualenv/pysyncml-2.7/bin/activate

test:
	@echo "[  ] running nosetest (without coverage)..."
	$(NOSE) --verbose --where src

cover:
	@echo "[  ] running nosetest with coverage..."
	$(NOSE) --with-coverage \
	  --cover-erase \
	  --cover-package=pysyncml \
	  --verbose --where src

#	  --cover-html --cover-html-dir=coverage \
#	  --cover-branches

pkg:
	@echo "[  ] building python distribution egg..."
	$(PY26) && python setup.py bdist_egg
	$(PY27) && python setup.py bdist_egg
	$(PY27) && python setup.py sdist

# pkg-prod:
# 	@echo "[  ] building python production distribution egg..."
# 	# NOTE: this does not seem to work with setuptools 0.6c12
# 	python setup.py --no-svn-revision --no-date --tag-build-name "" bdist_egg

upload: upload-pypi upload-sf upload-docs

upload-pypi:
	@echo "[  ] building and uploading python distribution egg..."
	$(PY26) && python setup.py bdist_egg upload
	$(PY27) && python setup.py bdist_egg upload
	$(PY27) && python setup.py sdist upload

upload-sf:
	@echo "[  ] uploading distributions to sourceforge..."
	$(RSYNC) -avz --rsh ssh --filter '- .svn' \
	  dist/ $(RSYNCUSER)@frs.sourceforge.net:/home/frs/project/pysyncml/trunk

docs:
	@echo "[  ] building HTML documentation..."
	mkdir -p sphinx/build
	$(SPHINX) -b html -c sphinx -d sphinx/build src doc
# TODO: perhaps convert to using setup.py for this?
#       the problem that i had was that i was getting a very confusing
#         error: sphinx/conf.py: No such file or directory
#       (but the file clearly existed)
#	python setup.py build_sphinx

upload-docs:
	@echo "[  ] uploading HTML documentation..."
	python setup.py upload_docs

deploy: docs upload

# cheesecake:
# 	@echo "[  ] testing the kwalitee of pysyncml..."
# 	cheesecake_index --name=svnpublish

clean:
	find src/pysyncml -iname '*.pyc' -exec rm {} \;
	rm -fr sphinx/build/* build/*

#------------------------------------------------------------------------------
# end of $Id: Makefile 34 2012-07-03 02:48:00Z griff1n $
#------------------------------------------------------------------------------
