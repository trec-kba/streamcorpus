'''
basic tests for the streamcorpus package
'''
from __future__ import absolute_import


def test_streamcorpus():
    import streamcorpus
    from streamcorpus import EntityType
    print streamcorpus.EntityType._VALUES_TO_NAMES
