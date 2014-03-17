python streamcorpus
===================

python wrapper around the streamcorpus interfaces:

   http://github.com/trec-kba/streamcorpus

To generate new python files from an updated thirft definition run the
following command:

   python setup.py thrift

Under the hood this runs

    thrift --gen py streamcorpus-v0_3_0.thrift

and integrates the generated code into this package.

