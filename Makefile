
# For recursive invocation of Make see:
#   http://www.gnu.org/software/make/manual/html_node/Phony-Targets.html#Phony-Targets 
SUBDIRS = src 

python:
	thrift --gen py:new_style,slots --out py/src/streamcorpus if/streamcorpus.thrift 
	thrift --gen py:new_style,slots --out py/src/streamcorpus if/streamcorpus-v0_1_0.thrift
	cd src/python && $(MAKE)

cpp:
	thrift --gen cpp  --out cpp if/streamcorpus.thrift 
	# Elected to use cmake here as it is cross platform and simple
	cmake cpp/CMakeLists.txt
	cd cpp && $(MAKE)

clean: 
	cd py && $(MAKE) clean
	cd cpp && $(MAKE) clean
