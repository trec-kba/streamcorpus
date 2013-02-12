
clean:
	rm -f src/streamcorpus/ttypes.py
	rm -f src/streamcorpus/constants.py
	rm -f src/streamcorpus/ttypes_v0_1_0.py
	rm -f src/streamcorpus/constants_v0_1_0.py
	rm -rf build dist

install: build
	## I think this `clean --all` step removes existing versions
	## from site-packages that would conflict when we install
	python setup.py clean --all
	python setup.py install

build_eggs: build
	python setup.py bdist_egg

build_packages: build_eggs
	python setup.py bdist_rpm

