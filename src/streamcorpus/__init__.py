#!/usr/bin/python
'''
Tools for processing a Stream Corpus
'''

import re
import time
import hashlib
from cStringIO import StringIO

## import the thrift library
from thrift import Thrift
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

## import the KBA-specific thrift types
from ttypes import StreamItem, ContentItem, Label, StreamTime, Offset

def make_stream_time(zulu_timestamp):
    '''
    Make a StreamTime object for a zulu_timestamp in this format:
    '2000-01-01T12:34:00.000123Z'
    This computes the equivalent epoch_ticks, so you don't have to.
    '''
    st = StreamTime(zulu_timestamp=zulu_timestamp)
    ## for reference http://www.epochconverter.com/
    st.epoch_ticks = time.mktime(time.strptime(
            zulu_timestamp, 
            '%Y-%m-%dT%H:%M:%S.%fZ')) - time.timezone
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
    si.stream_time = st
    si.abs_url = abs_url
    si.doc_id = hashlib.md5(abs_url).hexdigest()
    si.stream_id = '%d-%s' % (st.epoch_ticks, si.doc_id)
    return si

class Chunk(object):
    '''
    A serialized batch of StreamItem instances.
    '''
    def __init__(self, data=None, file_obj=None):
        '''
        Load a chunk from an existing file handle or buffer of data.
        If no data is passed in, then chunk starts as empty and
        chunk.add(stream_item) can be called to append to it.
        '''
        self._count = 0
        self._o_protocol = None
        self._o_transport = None
        if data is None and file_obj is None:
            ## Make output file obj for thrift, wrap in protocol
            self._o_transport = StringIO()
            self._o_protocol = TBinaryProtocol.TBinaryProtocol(self._o_transport)

        elif file_obj is None:
            ## wrap it in a file obj
            file_obj = StringIO(data)
            file_obj.seek(0)

        ## set _chunk_fh, possibly to None
        self._chunk_fh = file_obj

    def add(self, stream_item):
        'add stream_item object to chunk'
        assert self._o_protocol, 'cannot add to a Chunk instantiated with data'
        stream_item.write(self._o_protocol)
        self._count += 1

    def __str__(self):
        'get the byte array of thrift data'
        if self._o_transport is None:
            return ''
        self._o_transport.seek(0)
        o_thrift_data = self._o_transport.getvalue()
        return o_thrift_data

    def __len__(self):
        ## how to make this pythonic given that we have __iter__?
        return self._count

    def __iter__(self):
        '''
        Iterator over StreamItems in the chunk
        '''
        assert self._chunk_fh, 'cannot iterate over stream_items in an empty Chunk'
        ## seek to the start, so can iterate multiple times over the chunk
        self._chunk_fh.seek(0)
        ## wrap the file handle in buffered transport
        i_transport = TTransport.TBufferedTransport(self._chunk_fh)
        ## use the Thrift Binary Protocol
        i_protocol = TBinaryProtocol.TBinaryProtocol(i_transport)

        ## read StreamItem instances until input buffer is exhausted
        while 1:

            ## instantiate a StreamItem instance 
            doc = StreamItem()

            try:
                ## read it from the thrift protocol instance
                doc.read(i_protocol)

                ## yield is python primitive for iteration
                yield doc

            except EOFError:
                break

class TokenizationException(Exception):
    pass

class Token(object):
    '''
    base class for tokens to be emitted from the tokens and sentences
    iterators.
    '''        
    __slots__ = [
        'token_number',       ## zero-based index into the stream of
                              ## tokens from a document, does not
                              ## count sentence boundaries as tokens.

        'sentence_number',    ## zero-based index into the stream of
                              ## sentences from a document.  Each
                              ## sentence contains one or more tokens.

        'sentence_position',  ## zero-basd index into the sentence

        'token',              ## the actual token string

        'lemma',              ## lemmatization of the token

        'pos',                ## part of speech tagging

        'entity_type',        ## from named entity classifier

        'start_byte',         ## in original input text

        'end_byte',           ## in original input text

        'parent_id',          ## parent sentence_position in
                              ## dependency parse of sentence

        'dependency_path',    ## label on path to parent

        'equivalence_id',     ## for in-doc coref

        'labels',             ## array of instances of Label attached
                              ## to this token
        ]

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
