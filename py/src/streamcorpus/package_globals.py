#!/usr/bin/env python

# This used to be __init__.py for streamcorpus, but then we wanted to
# make streamcorpus.pipeline a 'namespace' package so that other
# source distributions could add their modules under it. But then we
# discovered that we need to make streamcorpus package a namespace
# package as well. BUT, there's a bunch of existing code out in the
# wild that depends on utility functions (below) as streamcorpus.Chunk
# & etc.
#
# SO, the new streamcorpus/__init__.py MUST be copied EXACTLY
# to any new source distribution seeking to put code in the
# streamcorpus namespace heirarchy.
#
# pkg_resources.declare_namespaces finds all __init__.py sources under
# the package from all its install locations and runs them all. They
# all run with the same locals() context. locals() is effectively
# 'this' for the module. While we're loading the __init__.py that
# lives next to this package_globals.py we need to notice that and
# branch on the stack to import all the symbols from this module after
# finishing the namespacing process.
#
# As long as no other source distribution defines
# streamcorpus/package_globals.py we're fine.
#
# This is all a weird hack. Java and other package systems don't seem
# to have these hangups.
'''
Python module of convenience functions around the structures defined
in streamcorpus.thrift

.. This software is released under an MIT/X11 open source license.
   Copyright 2012-2014 Diffeo, Inc.
'''

import re
from time import mktime
import time
import hashlib
from datetime import datetime
from cStringIO import StringIO

## import the KBA-specific thrift types
from ttypes import StreamItem, ContentItem, Label, StreamTime, \
    Offset, Rating, Annotator, Versions, Token, Sentence, EntityType, \
    Tagging, OffsetType, Target, \
    Language, \
    MentionType, AttributeType, Attribute, Gender, \
    RelationType, FlagType

## unambiguous name for the current one
StreamItem_v0_3_0 = StreamItem

from ttypes_v0_1_0 import StreamItem as StreamItem_v0_1_0
from ttypes_v0_2_0 import StreamItem as StreamItem_v0_2_0
import ttypes_v0_1_0
import ttypes_v0_2_0

from _chunk import Chunk, PickleChunk, JsonChunk, \
    parse_file_extensions, known_compression_schemes, \
    decrypt_and_uncompress, compress_and_encrypt, \
    compress_and_encrypt_path, \
    serialize, deserialize, \
    VersionMismatchError
from _cbor_chunk import CborChunk

__all__ = ['Chunk', 'PickleChunk', 'JsonChunk', 'CborChunk',
           'decrypt_and_uncompress', 'compress_and_encrypt',
           'compress_and_encrypt_path',
           'parse_file_extensions',
           'known_compression_schemes',
           'serialize', 'deserialize',
           'make_stream_time', 'make_stream_item',
           'get_entity_type',
           'get_date_hour',
           'add_annotation',
           'StreamItem', 'ContentItem', 'Label', 'StreamTime',
           'Offset', 'Rating', 'Annotator', 'Versions', 'Token', 'Sentence', 'EntityType',
           'Target',
           'Tagging', 'OffsetType',
           'Language',
           'MentionType',
           'Attribute',
           'AttributeType',
#           'Relation',
           'RelationType', 'FlagType',
           'Gender',
           'StreamItem_v0_1_0',
           'StreamItem_v0_2_0',
           'StreamItem_v0_3_0',
           'ttypes_v0_1_0',
           'ttypes_v0_2_0',
           'VersionMismatchError',
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


def get_epoch_ticks_for_date_hour(date_hour):
    '''
    Returns an epoch_ticks int for the start of a date_hour string
    '''
    parts = date_hour.split('-')
    assert len(parts) == 4
    zt = '-'.join(parts[:3]) + 'T' + parts[3] + ':00:00.000000Z'
    return make_stream_time(zt).epoch_ticks


def make_stream_time(zulu_timestamp=None, epoch_ticks=None):
    '''
    Creates a StreamTime object from either a string or a unix-time number.
    string should be formatted like '2000-01-01T12:34:00.000123Z'
    zulu_timestamp can be either a string or a number
    epoch_ticks must be int, long, or float
    zulu_timestamp is type detected so that it can be passed through from the sole zulu_timestamp parameter of make_stream_item() below
    '''
    if zulu_timestamp is not None:
        if isinstance(zulu_timestamp, basestring):
            return _stream_time_from_string(zulu_timestamp)
        if isinstance(zulu_timestamp, (int,long,float)):
            return _stream_time_from_number(zulu_timestamp)
    if epoch_ticks is not None:
        return _stream_time_from_number(epoch_ticks)
    return _stream_time_from_string(None)


_zulu_timestamp_format = '%Y-%m-%dT%H:%M:%S.%fZ'


def _stream_time_from_number(epoch_ticks):
    '''
    Make a StreamTime object from a utc unix time number.
    '''
    then = datetime.utcfromtimestamp(epoch_ticks)
    return StreamTime(
        zulu_timestamp=then.strftime(_zulu_timestamp_format),
        epoch_ticks=epoch_ticks)


from calendar import timegm

def _stream_time_from_string(zulu_timestamp):
    '''
    Make a StreamTime object for a zulu_timestamp in this format:
    '2000-01-01T12:34:00.000123Z'
    This computes the equivalent epoch_ticks, so you don't have to.

    If zulu_timestamp is not specified, it defaults to UTC now.
    '''
    ## see this reference
    # http://aboutsimon.com/2013/06/05/datetime-hell-time-zone-aware-to-unix-timestamp/
    if zulu_timestamp is None:
        then = datetime.utcnow()
        timestamp = timegm(then.timetuple())
    else:
        then = time.strptime(
             zulu_timestamp.replace('Z', 'GMT'),
            _zulu_timestamp_format.replace('Z', '%Z')
            )
        timestamp = timegm(then)
    return StreamTime(
        zulu_timestamp=zulu_timestamp,
        epoch_ticks=timestamp)


def make_stream_item(zulu_timestamp, abs_url, version=Versions.v0_3_0):
    '''
    Assemble a minimal StreamItem with internally consistent
    .stream_time.zulu_timestamp, .stream_time.epoch_ticks, .abs_url,
    .doc_id, and .stream_id

    zulu_timestamp may be either a unix-time number or a string like '2000-01-01T12:34:00.000123Z'
    '''
    st = make_stream_time(zulu_timestamp)
    if version == Versions.v0_3_0:
        si = StreamItem_v0_3_0()
        ## create an empty .body attribute and .body.language
        si.body = ContentItem(language=Language(code='', name=''))
    elif version == Versions.v0_2_0:
        si = StreamItem_v0_2_0()
        ## create an empty .body attribute and .body.language
        si.body = ttypes_v0_2_0.ContentItem(
            language=ttypes_v0_2_0.Language(code='', name=''))
    si.version = version
    si.stream_time = st
    ## Always start with an abs_url and only move it to original_url
    ## if some fetching process decides that the URL needs repair.
    si.abs_url = abs_url
    si.doc_id = hashlib.md5(abs_url).hexdigest()
    si.stream_id = '%d-%s' % (st.epoch_ticks, si.doc_id)
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

def get_entity_type(tok):
    '''
    returns the string name of the EntityType on this token, or None
    if it is not set.  If Token.entity_type == CUSTOM_TYPE, then this
    returns the Token.custom_entity_type string instead of
    streamcorpus.EntityType._VALUES_TO_NAMES
    '''
    if tok.entity_type is None:
        return None
    elif tok.entity_type == EntityType.CUSTOM_TYPE:
        if tok.custom_entity_type is None:
            logger.critical('Token.entity_type == CUSTOM_TYPE but Token.custom_entity_type is None!')
        return tok.custom_entity_type
    else:
        return EntityType._VALUES_TO_NAMES[tok.entity_type]
