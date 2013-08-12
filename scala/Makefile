## constructs a scala package and puts it into a jar, also runs a
## simple test in src/test/scala/streamcorpus/Test.scala

TMP=/tmp/scala-streamcorpus-build
VER=$(shell cat ../if/VERSION)

OUTPUT_JAR=streamcorpus-scala-v$(VER).jar

export GEN_CLASSPATH=lib/util-core_2.10-6.3.8.jar:lib/scopt_2.10-2.1.0.jar:lib/scrooge-core_2.10-3.5.0.jar:lib/scrooge-generator_2.10-3.5.0.jar:lib/commons-lang-2.6.jar
export CLASSPATH=lib/libthrift-1.0.0.jar:../java/lib/slf4j-api-1.7.2.jar:../java/lib/slf4j-simple-1.7.2.jar:lib/scrooge-core_2.10-3.5.0.jar:lib/scrooge-runtime_2.10-3.5.0.jar:./$(OUTPUT_JAR)

compile:
	## compile the "streamcorpus" scala package
	scala -cp $(GEN_CLASSPATH) com.twitter.scrooge.Main ../if/streamcorpus-v0_3_0.thrift

build: # compile
	## compile classes and test programs
	rm -rf $(TMP)
	mkdir -p $(TMP)/classes
	scalac -d $(TMP)/classes streamcorpus/*

	## put into a jar
	cd $(TMP)/classes && jar cvf ../$(OUTPUT_JAR) *

	## put the jar into this repo
	mv $(TMP)/$(OUTPUT_JAR) .

compile_test:
	mkdir -p $(TMP)/classes
	scalac -d $(TMP)/classes src/test/scala/streamcorpus/*

test:  compile_test
	scala -cp $(TMP)/classes:$(CLASSPATH) Test
	rm -rf $(TMP)
