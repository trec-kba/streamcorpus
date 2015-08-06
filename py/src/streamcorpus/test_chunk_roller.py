'''Tests for ChunkRoller

.. Your use of this software is governed by your license agreement.
   Unpublished Work Copyright 2015 Diffeo, Inc.
'''

import os

from streamcorpus import ChunkRoller, make_stream_item


def test_chunk_roller(tmpdir):

    cr = ChunkRoller(str(tmpdir), chunk_max=10)

    for i in range(25):
        si = make_stream_item(i, str(i))
        
        cr.add(si)

    cr.close()

    files = []
    for fname in os.listdir(str(tmpdir)):
        assert 'tmp' not in fname
        count = int(fname.split('-')[0])
        files.append(count)

    assert sorted(files) == [5, 10, 10]
