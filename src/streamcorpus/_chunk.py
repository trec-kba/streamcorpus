#!/usr/bin/env python
'''
Provides a reader/writer for batches of streamcorpus.StreamItem
instances stored in flat files using Thrift.

This software is released under an MIT/X11 open source license.

Copyright 2012 Diffeo, Inc.
'''

## import the thrift library
from thrift import Thrift
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

import os
from cStringIO import StringIO

from .ttypes import StreamItem, ContentItem, Label, StreamTime, Offset, Rating, Annotator

class Chunk(object):
    '''
    reader/writer for batches of streamcorpus.StreamItem instances
    stored in flat files using Thrift
    '''
    def __init__(self, path=None, data=None, file_obj=None, mode='rb'):
        '''
        Load a chunk from an existing file handle or buffer of data.
        If no data is passed in, then chunk starts as empty and
        chunk.add(stream_item) can be called to append to it.

        mode is only used if you specify a path to an existing file to
        open.
        '''
        self._count = 0
        self._o_chunk_fh = None
        self._o_protocol = None
        self._o_transport = None

        ## open an existing file from path, or create it
        if path is not None:
            assert data is None and file_obj is None, \
                'Must specify only path or data or file_obj'
            if os.path.exists(path):
                ## if the file is there, then use mode 
                file_obj = open(path, mode)
            else:
                ## otherwise make one for writing
                assert mode == 'wb', \
                    '%s does not exist but mode=%r' % (path, mode)
                file_obj = open(path, 'wb')

        ## if created without any arguments, then prepare to add
        ## stream_items to an in-memory file object
        if data is None and file_obj is None:
            ## Make output file obj for thrift, wrap in protocol
            self._o_transport = StringIO()
            self._o_protocol = TBinaryProtocol.TBinaryProtocol(self._o_transport)

        elif file_obj is None:
            ## wrap the data in a file obj for reading
            file_obj = StringIO(data)
            file_obj.seek(0)

        elif file_obj is not None and 'w' in file_obj.mode:
            ## use the file object for writing out the data as it
            ## happens, i.e. in streaming mode.
            self._o_chunk_fh = file_obj            
            self._o_transport = TTransport.TBufferedTransport(self._o_chunk_fh)
            self._o_protocol = TBinaryProtocol.TBinaryProtocol(self._o_transport)
            ## this causes _i_chunk_fh to be None below
            file_obj = None

        ## set _i_chunk_fh, possibly to None
        self._i_chunk_fh = file_obj

    def add(self, stream_item):
        'add stream_item object to chunk'
        assert self._o_protocol, 'cannot add to a Chunk instantiated with data'
        stream_item.write(self._o_protocol)
        self._count += 1

    def close(self):
        '''
        Close any chunk file that we might have had open for writing.
        '''
        if self._o_chunk_fh is not None:
            self._o_transport.flush()
            self._o_chunk_fh.close()

    def __del__(self):
        '''
        If garbage collected, try to close.
        '''
        self.close()

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
        assert self._i_chunk_fh, 'cannot iterate over a Chunk open for writing'
        ## seek to the start, so can iterate multiple times over the chunk
        self._i_chunk_fh.seek(0)
        ## wrap the file handle in buffered transport
        i_transport = TTransport.TBufferedTransport(self._i_chunk_fh)
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
