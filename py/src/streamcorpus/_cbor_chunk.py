#!/usr/bin/env python
'''
Provides a CBOR (RFC 7049) based Chunk implementation.

Attempts to load python package "cbor".
Doesn't block loading if not present, but raises exceptions at run time.

This software is released under an MIT/X11 open source license.

Copyright 2012 Diffeo, Inc.
'''

import StringIO
import cStringIO

from ._chunk import BaseChunk
try:
    import cbor
except:
    cbor = None


class BufferedReader(object):
    '''
    Wrap a file-like object from which we .read() in one which which buffers.
    '''
    _BUFSIZE = 32*1024
    def __init__(self, fp):
        self._fp = fp
        self.buf = None
        self.pos = 0

    def read(self, *args):
        if args:
            toread = args[0]
        else:
            toread = -1
        if toread == -1:
            rest = self._fp.read(-1)
            if self.buf is not None:
                rest = self.buf + rest
                self.buf = None
                self.pos = 0
            return rest

        have = ((self.buf is not None) and (len(self.buf) - self.pos)) or 0
        while have < toread:
            need = max(self._BUFSIZE, toread - have)
            assert need > 0
            got = self._fp.read(need)
            if not got:
                out = self.buf[self.pos:]
                self.buf = None
                self.pos = 0
                return out
            if self.buf is None:
                self.buf = got
            else:
                self.buf = self.buf[self.pos:] + got
            self.pos = 0
            have = ((self.buf is not None) and len(self.buf)) or 0

        out = self.buf[self.pos:self.pos+toread]
        self.pos += toread
        #self.buf = self.buf[toread:]
        return out


class CborChunk(BaseChunk):
    '''
    `message` must be a constructor or factory function that accepts the object from cbor.load() that results from cbor.dump(write_wrapper(msg))
    '''

    # These are known to be okay for a zillion little reads that the
    # CBOR library does. Other file-like-objects will get wrapped in a
    # BufferedReader
    #
    # Specifically things like lzma.open() and network sockets are
    # pretty terrible when accessed by a zillion little read()
    # operations.
    #
    # NOTE: Using BufferedReader assumes you're going to read the
    # stream through to the end. Stopping in the middle will leave
    # some random fraction of input in the BufferedReader and that
    # would be lost and break the stream.
    _OK_RAW_INPUTS = (file, BufferedReader, StringIO.StringIO, type(cStringIO.StringIO()))

    def __init__(self, *args, **kwargs):
        super(CborChunk, self).__init__(*args, **kwargs)

    def write_msg_impl(self, msg):
        assert self._o_chunk_fh is not None
        cbor.dump(msg, self._o_chunk_fh)

    def read_msg_impl(self):
        assert self._i_chunk_fh is not None
        if not isinstance(self._i_chunk_fh, self._OK_RAW_INPUTS):
            self._i_chunk_fh = BufferedReader(self._i_chunk_fh)
        while True:
            try:
                ob = cbor.load(self._i_chunk_fh)
                msg = self.message(ob)
                yield msg
            except EOFError:
                # okay. done.
                return


if cbor is None:
    # clobber definition with something that just errors out on attempt to use
    class MissingCbor(BaseChunk):
        def __init__(self, *args, **kwargs):
            raise Exception('package cbor is not installed')

        def write_msg_impl(self, msg):
            raise Exception('package cbor is not installed')
        def read_msg_impl(self):
            raise Exception('package cbor is not installed')

    CborChunk = MissingCbor
