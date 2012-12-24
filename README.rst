streamcorpus
============

streamcorpus.thrift defines the structs for documents with timestamps
and metadata, such as annotation and auto-generated tagging.

The streamcorpus python module is built around the results of running
thrift --gen py streamcorpus.thrift, which is done for you in the
Makefile.
