#!/usr/bin/env python
'''
Provides a CBOR (RFC 7049) based Chunk implementation.

Attempts to load python package "cbor".
Doesn't block loading if not present, but raises exceptions at run time.

This software is released under an MIT/X11 open source license.

Copyright 2012 Diffeo, Inc.
'''

from ._chunk import BaseChunk
try:
    import cbor
except:
    cbor = None


class CborChunk(BaseChunk):
    '''
    `message` must be a constructor or factory function that accepts the object from cbor.load() that results from cbor.dump(write_wrapper(msg))
    '''
    def __init__(self, *args, **kwargs):
        super(CborChunk, self).__init__(*args, **kwargs)

    def write_msg_impl(self, msg):
        assert self._o_chunk_fh is not None
        cbor.dump(msg, self._o_chunk_fh)

    def read_msg_impl(self):
        assert self._i_chunk_fh is not None
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

