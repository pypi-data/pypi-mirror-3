#
# Makefile for PyPoly Jinja plugin
#

.PHONY: build build25 build26 build27 build_dev clean check_pep8 remove_whitespace

ARCHIVE_VERSION=HEAD
ARCHIVE_PREFIX=pypoly-plugin-jinja_${ARCHIVE_VERSION}
ARCHIVE_NAME=pypoly-plugin-jinja_${ARCHIVE_VERSION}
ARCHIVE_PATH=

BIN_PATH=/usr/bin/

build: build25 build26 build27

build25:
	@echo -n "Building EGG for Python 2.5 ..."
	@if [ -x "${BIN_PATH}python2.5" ] ; then \
		"${BIN_PATH}python2.5" setup.py bdist_egg > /dev/null;\
		echo "done";\
	else \
		echo "Python 2.5 not found"; \
	fi 

build26:
	@echo -n "Building EGG for Python 2.6 ..."
	@if [ -x "${BIN_PATH}python2.6" ] ; then \
		"${BIN_PATH}python2.6" setup.py bdist_egg > /dev/null;\
		echo "done";\
	else \
		echo "Python 2.6 not found"; \
	fi 

build27:
	@echo -n "Building EGG for Python 2.7 ..."
	@if [ -x "${BIN_PATH}python2.7" ] ; then \
		"${BIN_PATH}python2.7" setup.py bdist_egg > /dev/null;\
		echo "done";\
	else \
		echo "Python 2.7 not found"; \
	fi 

	
build_archive:
	git archive --format=tar --prefix=${ARCHIVE_PREFIX}/ ${ARCHIVE_VERSION} | gzip -9 > ${ARCHIVE_PATH}${ARCHIVE_NAME}.tar.gz
	git archive --format=tar --prefix=${ARCHIVE_PREFIX}/ ${ARCHIVE_VERSION} | bzip2 -9 > ${ARCHIVE_PATH}${ARCHIVE_NAME}.tar.bz2
	git archive --format=zip --prefix=${ARCHIVE_PREFIX}/ ${ARCHIVE_VERSION}  > ${ARCHIVE_PATH}${ARCHIVE_NAME}.zip

build_dev:
	@echo "Building development egg"
	@python setup.py develop --install-dir .. -m

clean:
	@echo "Cleaning ..."
	@find . -name \*\.pyc -exec rm -v {} \;
	@rm -rf build dist

check_pep8:
	@echo "Checking PEP8 ..."
	@pep8 -r --statistics pp_jinja2

remove_whitespace:
	# remove whitespaces at the end of a line
	find ./pp_jinja2 -name '*.py' -exec sed -i 's/[ \t]*$$//' {} \;
