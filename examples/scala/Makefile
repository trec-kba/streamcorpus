TMP=/tmp/scala-streamcorpus-build
VER=$(shell cat ../if/VERSION)

LIB_JAR=streamcorpus-scala-v0_3_0.jar

export CLASSPATH=../../scala/lib/util-core-6.1.0.jar:../../scala/lib/libthrift-1.0.0.jar:../../java/lib/slf4j-api-1.7.2.jar:../../java/lib/slf4j-simple-1.7.2.jar:../../scala/$(LIB_JAR):../../scala/lib/scrooge-core_2.10-3.5.0.jar:../../scala/lib/scrooge-generator_2.10-3.5.0.jar:../../scala/lib/scrooge-runtime_2.10-3.5.0.jar

TMP=/tmp/scala-streamcorpus-example-build

clean:
	rm -rf $(TMP)

build: clean
	mkdir -p $(TMP)/classes
	scalac -d $(TMP)/classes streamcorpus_example/AddTagging.scala

test: build
	scala -cp $(TMP)/classes:$(CLASSPATH) streamcorpus_example.AddTagging
