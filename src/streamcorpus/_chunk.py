#!/usr/bin/env python
'''
Provides a reader/writer for batches of Thrift messages stored in flat
files.

Defaults to streamcorpus.StreamItem and can be used with any
Thrift-defined objects.

This software is released under an MIT/X11 open source license.

Copyright 2012 Diffeo, Inc.
'''

## import the thrift library
from thrift import Thrift
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

import os
from cStringIO import StringIO

from .ttypes import StreamItem

class Chunk(object):
    '''
    reader/writer for batches of Thrift messages stored in flat files.
    '''
    def __init__(self, path=None, data=None, file_obj=None, mode='rb',
                 message=StreamItem):
        '''
        Load a chunk from an existing file handle or buffer of data.
        If no data is passed in, then chunk starts as empty and
        chunk.add(message) can be called to append to it.

        mode is only used if you specify a path to an existing file to
        open.

        :param path: path to a file in the local file system

        :param mode: read/write mode for opening the file; if
        mode='wb', then a file will be created.

        :file_obj: already opened file, mode must agree with mode
        parameter.

        :param data: bytes of data from which to read messages

        :param message: defaults to StreamItem; you can specify your
        own Thrift-generated class here.
        '''
        ## class for constructing messages when reading
        self.message = message

        ## initialize internal state before figuring out what data we
        ## are acting on
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
        ## messages to an in-memory file object
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

    def add(self, msg):
        'add message instance to chunk'
        assert self._o_protocol, 'cannot add to a Chunk instantiated with data'
        msg.write(self._o_protocol)
        self._count += 1

    def close(self):
        '''
        Close any chunk file that we might have had open for writing.
        '''
        if self._o_chunk_fh is not None:
            self._o_transport.flush()
            self._o_chunk_fh.close()
            ## make this method idempotent
            self._o_chunk_fh = None

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
        Iterator over messages in the chunk
        '''
        assert self._i_chunk_fh, 'cannot iterate over a Chunk open for writing'

        ## seek to the start, so can iterate multiple times over the chunk
        try:
            self._i_chunk_fh.seek(0)
        except IOError:
            pass
            ## just assume that it is a pipe like stdin that need not
            ## be seeked to start

        ## wrap the file handle in buffered transport
        i_transport = TTransport.TBufferedTransport(self._i_chunk_fh)
        ## use the Thrift Binary Protocol
        i_protocol = TBinaryProtocol.TBinaryProtocol(i_transport)

        ## read message instances until input buffer is exhausted
        while 1:

            ## instantiate a message  instance 
            msg = self.message()

            try:
                ## read it from the thrift protocol instance
                msg.read(i_protocol)

                ## yield is python primitive for iteration
                yield msg

            except EOFError:
                break
