all:	build

clean:
	rm -rf gen-py
	rm -f src/streamcorpus/ttypes.py
	rm -f src/streamcorpus/constants.py
	rm -f src/streamcorpus/ttypes_v0_2_0.py
	rm -f src/streamcorpus/constants_v0_2_0.py
	rm -f src/streamcorpus/ttypes_v0_1_0.py
	rm -f src/streamcorpus/constants_v0_1_0.py
	rm -rf build dist src/streamcorpus_dev.egg-info
	rm -f runtests.py

.PHONY : build
build:
	python setup.py build

install:
	## I think this `clean --all` step removes existing versions
	## from site-packages that would conflict when we install
	#python setup.py clean --all
	python setup.py install

test:
	python setup.py test

build_eggs: build
	python setup.py bdist_egg

build_packages: build_eggs
	python setup.py bdist_rpm

register: build
	python setup.py sdist upload
