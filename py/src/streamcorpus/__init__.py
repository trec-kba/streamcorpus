#!/usr/bin/env python
'''
Python module of convenience functions around the structures defined
in streamcorpus.thrift

This software is released under an MIT/X11 open source license.

Copyright 2012 Diffeo, Inc.
'''

import re
import time
import hashlib
from datetime import datetime
from cStringIO import StringIO

## import the KBA-specific thrift types
from .ttypes import StreamItem, ContentItem, Label, StreamTime, \
    Offset, Rating, Annotator, Versions, Token, Sentence, EntityType, \
    Tagging, OffsetType, Target, \
    Language

from .ttypes_v0_1_0 import StreamItem as StreamItem_v0_1_0

from ._chunk import Chunk, decrypt_and_uncompress, compress_and_encrypt, \
    compress_and_encrypt_path, \
    serialize, deserialize

__all__ = ['Chunk', 'decrypt_and_uncompress', 'compress_and_encrypt', 
           'compress_and_encrypt_path', 
           'make_stream_time', 'make_stream_item',
           'get_date_hour',
           'StreamItem', 'ContentItem', 'Label', 'StreamTime', 
           'Offset', 'Rating', 'Annotator', 'Versions', 'Token', 'Sentence', 'EntityType', 
           'Target',
           'Tagging', 'OffsetType', 
           'Language',
           'StreamItem_v0_1_0',
           ]

def get_date_hour(stream_thing):
    '''
    Returns a date_hour string in the format '2000-01-01-12'
    :param stream_time: a StreamTime or StreamItem object
    '''
    if type(stream_thing) == StreamItem:
        stream_thing = stream_thing.stream_time

    assert type(stream_thing) == StreamTime, \
        'must be StreamTime or StreamItem, not %r <-- %r' \
        % (type(stream_thing), stream_thing)

    return stream_thing.zulu_timestamp.split(':')[0].replace('T', '-')


def make_stream_time(zulu_timestamp=None):
    '''
    Make a StreamTime object for a zulu_timestamp in this format:
    '2000-01-01T12:34:00.000123Z'
    This computes the equivalent epoch_ticks, so you don't have to.

    If zulu_timestamp is not specified, it defaults to UTC now.
    '''
    zulu_timestamp_format = '%Y-%m-%dT%H:%M:%S.%fZ'
    if zulu_timestamp is None:
        zulu_timestamp = datetime.utcnow().strftime(
            zulu_timestamp_format)
    st = StreamTime(zulu_timestamp=zulu_timestamp)
    ## for reference http://www.epochconverter.com/
    st.epoch_ticks = time.mktime(time.strptime(
            zulu_timestamp, 
            zulu_timestamp_format)) - time.timezone
    ## subtracting the time.timezone is crucial
    return st

def make_stream_item(zulu_timestamp, abs_url):
    '''
    Assemble a minimal StreamItem with internally consistent
    .stream_time.zulu_timestamp, .stream_time.epoch_ticks, .abs_url,
    .doc_id, and .stream_id
    '''
    st = make_stream_time(zulu_timestamp)
    si = StreamItem()
    si.version = Versions.v0_2_0
    si.stream_time = st
    ## Always start with an abs_url and only move it to original_url
    ## if some fetching process decides that the URL needs repair.
    si.abs_url = abs_url
    si.doc_id = hashlib.md5(abs_url).hexdigest()
    si.stream_id = '%d-%s' % (st.epoch_ticks, si.doc_id)
    ## create an empty .body attribute and .body.language
    si.body = ContentItem(language=Language(code='', name=''))
    return si

def add_annotation(data_item, *annotations):
    '''
    adds each item in annotations to data_item.labels or .ratings

    :type data_item: StreamItem, ContentItem, Sentence, Token
    :type labels_or_ratings: list of Rating or Label objects
    '''
    for anno in annotations:
        try:
            annotator_id = anno.annotator.annotator_id
        except Exception, exc:
            raise Exception('programmer error: passed a faulty annotation  %r' % exc)
        if isinstance(anno, Label):
            assert isinstance(data_item, (ContentItem, Sentence, Token)), data_item
            if annotator_id not in data_item.labels:
                data_item.labels[annotator_id] = []
            data_item.labels[annotator_id].append( anno )

        elif isinstance(anno, Rating):
            assert isinstance(data_item, StreamItem), data_item
            if annotator_id not in data_item.ratings:
                data_item.ratings[annotator_id] = []
            data_item.ratings[annotator_id].append( anno )

        else:
            raise Exception('programmer error: attempted add_annotation(%s...)' % type(data_item))

