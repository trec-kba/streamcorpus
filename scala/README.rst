Scala library
=============

To build and test the streamcorpus-scala-vXXX.jar, run

     make test


To see a simple example of iterating over tokens, read this:

     src/test/scala/streamcorpus/Test.scala


The Scrooge thrift compiler for Scala has some issues that one must be
careful about:

1) the "Scrooge" thrift compiler for Scala makes immutable objects
   from the incoming messages, which means that some copying is
   required to construct objects to which you can add new info.  See
   example in ../examples/scala for how to do this.

2) Scrooge also does a potentially annoying variable renaming, which
   is described in the comments of the example in ../examples/scala

