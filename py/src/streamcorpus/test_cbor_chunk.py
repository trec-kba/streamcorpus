from __future__ import absolute_import
from cStringIO import StringIO
import hashlib

from streamcorpus import CborChunk

def test_cbor_chunk():
    fh = StringIO()
    c = CborChunk(file_obj=fh, mode='wb', message=lambda x: x)
    c.add(dict(test='msg'))
    c.flush()

    data = fh.getvalue()
    assert hashlib.md5(data).hexdigest() == c.md5_hexdigest

    fh = StringIO(data)
    c = CborChunk(file_obj=fh, message=lambda x: x)
    msg = list(c)[0]
    assert msg['test'] == 'msg'

    assert hashlib.md5(data).hexdigest() == c.md5_hexdigest
