'''Utility class for spooling a stream of items to files on disk.
Initially, files flow into a temp file, which gets moved to a
permanent name when it reaches the `chunk_max` size or the stream
ends.

.. Your use of this software is governed by your license agreement.
   Unpublished Work Copyright 2015 Diffeo, Inc.
'''
from __future__ import absolute_import
import logging
import os
import random

from streamcorpus.ttypes import StreamItem
from streamcorpus._chunk import Chunk
from streamcorpus._cbor_chunk import CborChunk

logger = logging.getLogger(__name__)

class ChunkRoller(object):

    def __init__(self, chunk_dir, chunk_max=500, message=StreamItem):
        self.chunk_dir = chunk_dir
        self.chunk_max = chunk_max
        self.t_path = os.path.join(chunk_dir, 'tmp-%d.sc.xz'  % random.randint(0, 10**8))
        self.o_chunk = None
        self.message = message

    def add(self, si_or_fc):
        '''puts `si_or_fc` into the currently open chunk, which it creates if
        necessary.  If this item causes the chunk to cross chunk_max,
        then the chunk closed after adding.

        '''
        if self.o_chunk is None:
            if os.path.exists(self.t_path):
                os.remove(self.t_path)
            if self.message == StreamItem:
                self.o_chunk = Chunk(self.t_path, mode='wb')
            else:
                logger.info('Assuming CborChunk for message=%r', type(self.message))
                self.o_chunk = CborChunk(self.t_path, mode='wb')

        self.o_chunk.add(si_or_fc)
        logger.debug('added %d-th item to chunk', len(self.o_chunk))
        if len(self.o_chunk) == self.chunk_max:
            self.close()

    def close(self):
        if self.o_chunk:
            self.o_chunk.close()
            if self.message == StreamItem:
                extension = 'sc'
            else: 
                logger.warn('assuming file extension ".cbor"')
                extension = 'cbor'
            o_path = os.path.join(
                self.chunk_dir, 
                '%d-%s.%s.xz' % (len(self.o_chunk), self.o_chunk.md5_hexdigest, extension)
            )
            os.rename(self.t_path, o_path)
            self.o_chunk = None
            logger.info('rolled chunk to %s', o_path)

