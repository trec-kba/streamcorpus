#!/usr/bin/env python
'''
Tools for processing a Stream Corpus
'''

import re
import time
import hashlib
from datetime import datetime
from cStringIO import StringIO

## import the KBA-specific thrift types
from .ttypes import StreamItem, ContentItem, Label, StreamTime, \
    Offset, Rating, Annotator, Versions, Token, Sentence, EntityType, \
    Tagging
from ._chunk import Chunk

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
    si.version = Versions.v0_1_0
    si.stream_time = st
    si.abs_url = abs_url
    si.doc_id = hashlib.md5(abs_url).hexdigest()
    si.stream_id = '%d-%s' % (st.epoch_ticks, si.doc_id)
    return si

class TokenizationException(Exception):
    pass

sent_num_re = re.compile('<SENT id="(\d+)">')

def sentences(content_item):
    '''
    iterates over the content_item yielding arrays of Tokens
    '''
    sent_num = 0
    tok_num = 0
    def make_token(line):
        'construct a Token from a line of OWPL NER tagging'
        tok = Token()
        tok.token_number = tok_num
        tok.sentence_number = sent_num
        sent_pos, tok.token, begin_end, tok.pos, tok.entity_type, \
            tok.lemma, tok.dependency_path, tok.parent_id, equivalence_id = \
            line.split('\t')
        tok.sentence_position = int(sent_pos)
        tok.start_byte = int(begin_end.split(':')[0])
        tok.end_byte = int(begin_end.split(':')[1])
        tok.equivalence_id = int(equivalence_id)
        return tok

    this_sentence = []
    for line in content_item.ner.splitlines():
        if not line: continue
        if line.startswith('<SENT'):

            ## output the sentence
            yield map(make_token, this_sentence)

            sent_num = int(sent_num_re.match(line).group(1))

            ## reset
            this_sentence = []

        elif not line.startswith('</SENT'):
            this_sentence.append(line)
            tok_num += 1

    ## if last tok in doc was not boundary, then yield
    if this_sentence:
        ## output the last sentence
        yield map(make_token, this_sentence)
