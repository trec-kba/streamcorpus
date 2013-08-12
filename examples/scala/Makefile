## constructs a scala package and puts it into a jar, also runs a
## simple test in src/test/scala/streamcorpus/Test.scala

TMP=/tmp/scala-streamcorpus-build
VER=$(shell cat ../if/VERSION)

LIB_JAR=streamcorpus-scala-v0_3_0.jar

export CLASSPATH=../../scala/lib/scopt_2.9.1-2.0.1.jar:../../scala/lib/util-core-6.1.0.jar:../../scala/lib/libthrift-1.0.0.jar:../../java/lib/slf4j-api-1.7.2.jar:../../java/lib/slf4j-simple-1.7.2.jar:../../scala/$(LIB_JAR):../../scala/lib/scrooge-core_2.10-3.5.0.jar:../../scala/lib/scrooge-generator_2.10-3.5.0.jar:../../scala/lib/scrooge-runtime_2.10-3.5.0.jar

TMP=/tmp/scala-streamcorpus-example-build

clean:
	rm -rf $(TMP)

build: clean
	mkdir -p $(TMP)
	scalac -d $(TMP) AddTagging.scala

test: build
	cd $(TMP) && scala test.scala.streamcorpus.AddTagging
