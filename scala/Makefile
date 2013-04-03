
TMP=/tmp/scala-streamcorpus-build
VER=0.3.0

build:
	rm -rf $(TMP)
	export CLASSPATH=lib/libthrift-1.0.0.jar:lib/scrooge-runtime-3.0.7-SNAPSHOT.jar:lib/util-core-6.1.0.jar:../java/lib/slf4j-api-1.7.2.jar:../java/lib/slf4j-simple-1.7.2.jar
	mkdir -p $(TMP)/classes
	scalac -d $(TMP)/classes src/main/scala/streamcorpus/* src/test/scala/streamcorpus/*
	cd $(TMP)/classes && jar cvf ../streamcorpus-v$(VER).jar *

test:
	export CLASSPATH=lib/libthrift-1.0.0.jar:lib/scrooge-runtime-3.0.7-SNAPSHOT.jar:lib/util-core-6.1.0.jar:../java/lib/slf4j-api-1.7.2.jar:../java/lib/slf4j-simple-1.7.2.jar:$(TMP)/streamcorpus-v$(VER).jar
	scala Test
