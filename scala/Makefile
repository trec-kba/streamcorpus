## constructs a scala package and puts it into a jar, also runs a
## simple test in src/test/scala/streamcorpus/Test.scala

TMP=/tmp/scala-streamcorpus-build
VER=$(shell cat ../if/VERSION)

OUTPUT_JAR=streamcorpus-scala-v$(VER).jar

export CLASSPATH=lib/scopt_2.9.1-2.0.1.jar:lib/util-core-6.1.0.jar:lib/libthrift-1.0.0.jar:../java/lib/slf4j-api-1.7.2.jar:../java/lib/slf4j-simple-1.7.2.jar:./$(OUTPUT_JAR):lib/scrooge-core_2.10-3.5.0.jar:lib/scrooge-generator_2.10-3.5.0.jar:lib/scrooge-runtime_2.10-3.5.0.jar

compile:
	## compile the "streamcorpus" scala package
	scala com.twitter.scrooge.Main ../if/streamcorpus-v0_3_0.thrift

build: # compile
	## compile classes and test programs
	rm -rf $(TMP)
	mkdir -p $(TMP)/classes
	scalac -d $(TMP)/classes streamcorpus/* src/test/scala/streamcorpus/*

	## put into a jar
	cd $(TMP)/classes && jar cvf ../$(OUTPUT_JAR) *

	## put the jar into this repo
	mv $(TMP)/$(OUTPUT_JAR) .

test: # build
	scala test.scala.streamcorpus.AddTagging
	rm -rf $(TMP)
