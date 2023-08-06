#
# Makefile de construction de l'archive 
#


all: test sdist

clean:
	rm -f MANIFEST
	rm -f `find . -name \*.pyc`
	rm -f `find . -name \*~`
	rm -rf CartesInitProg.egg-info

sdist: clean
	python setup.py sdist

test:
	sh testall.sh

upload: clean
	python setup.py sdist --format=zip,gztar upload

commit: clean test
	svn commit

# eof
