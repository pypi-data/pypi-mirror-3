##
## Makefile (for developers)
##

egg:
	python2.4 setup.py bdist_egg --dist-dir .
	python2.5 setup.py bdist_egg --dist-dir .
	rm -rf build/ src/soho.egg-info/

register:
	python2.4 setup.py register

upload:
	python2.4 setup.py bdist_egg --dist-dir . upload
	python2.5 setup.py bdist_egg --dist-dir . upload
	rm -rf build/ src/soho.egg-info/

clean:
	rm -f *.egg