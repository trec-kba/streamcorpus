all:	build

clean:
	rm -rf gen-py
	rm -rf build dist src/streamcorpus_dev.egg-info
	rm -f runtests.py

.PHONY : build
build: clean
	python setup.py build sdist bdist_egg

install: build
	python setup.py install

test: install
	python setup.py test

register: build
	python setup.py sdist upload
