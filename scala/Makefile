## constructs a scala package and puts it into a jar, also runs a
## simple test in src/test/scala/streamcorpus/Test.scala

TMP=/tmp/scala-streamcorpus-build
VER=$(shell cat ../if/VERSION)

OUTPUT_JAR=streamcorpus-scala-v$(VER).jar

export CLASSPATH=lib/scrooge-generator-3.0.7-SNAPSHOT.jar:lib/scopt_2.9.1-2.0.1.jar:lib/util-core-6.1.0.jar:lib/libthrift-1.0.0.jar:lib/scrooge-runtime-3.0.7-SNAPSHOT.jar:../java/lib/slf4j-api-1.7.2.jar:../java/lib/slf4j-simple-1.7.2.jar:./$(OUTPUT_JAR)

compile:
	## compile the "streamcorpus" scala package
	scala com.twitter.scrooge.Main ../if/streamcorpus.thrift

build: compile
	## compile classes and test programs
	rm -rf $(TMP)
	mkdir -p $(TMP)/classes
	scalac -d $(TMP)/classes src/main/scala/streamcorpus/* src/test/scala/streamcorpus/*

	## put into a jar
	cd $(TMP)/classes && jar cvf ../$(OUTPUT_JAR) *

	## put the jar into this repo
	mv $(TMP)/$(OUTPUT_JAR) .

test: build
	scala Test
	rm -rf $(TMP)