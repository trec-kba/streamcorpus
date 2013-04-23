streamcorpus
============

Discussion forum:  https://groups.google.com/forum/#!forum/streamcorpus

streamcorpus provides a common data interchange format for document
processing pipelines that apply natural language processing tools to
large streams of text.  It offers these benefits:

* Based on Thrift, so is fast to serialize/deserialize and has
  easy-to-use language bindings for many languages.

* Convenience methods for serializing batches of documents into flat
  files, which we call Chunks.  For example, the TREC KBA corpus is
  stored in streamcorpus.Chunk files, see http://trec-kba.org/

* Unifies NLP data structures so that one pipeline can use different
  taggers in a unified way.  For example, tokenization, sentence
  chunking, entity typing, human-generated annotation, and offsets are
  all defined such that output from most tagging tools can be easily
  transformed into streamcorpus structures.  It is currently in use
  with LingPipe and Stanford CoreNLP, and we are working towards
  testing with more.

* Once a StreamItem has one or more sets of tokenized Sentence arrays,
  one can easily run downstream analytics that leverage the attributes
  on the token stream.

* Makes timestamping a central part of corpus organization, because
  every corpus is inherently anchored in history.  Streaming data is
  increasingly important in many applications.

* Has basic versioning and builds on Thrift's extensibility.


See if/streamcorpus.thrift for details.

See py/ for a python module built around the results of running
`thrift --gen py streamcorpus.thrift`, which is done py/Makefile

If you are interested in building a streamcorpus package around the
Thrift generated code for another language, please post to the
discussion forum: https://groups.google.com/forum/#!forum/streamcorpus