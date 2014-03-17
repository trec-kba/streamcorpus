'''
basic tests for the streamcorpus package
'''
from __future__ import absolute_import

import streamcorpus

def test_streamcorpus():
    from streamcorpus import EntityType
    print streamcorpus.EntityType._VALUES_TO_NAMES

def test_streamcorpus_flags():
    rating = streamcorpus.Rating()
    rating.flags = [streamcorpus.FlagType.PROFILE]
    assert 0 in rating.flags
