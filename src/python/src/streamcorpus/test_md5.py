
import uuid
from . import make_stream_item, ContentItem, Chunk
from cStringIO import StringIO
from _chunk import md5_file
import hashlib

def test_md5():
    _data = 'foo' * 100

    fh = StringIO( _data )
    mfh = md5_file(fh)

    data = mfh.read()
    dmd5 = hashlib.md5(data).hexdigest()

    assert dmd5 == mfh.md5_hexdigest, \
        (dmd5, mfh.md5_hexdigest)

    fh = StringIO()
    mfh = md5_file(fh)
    mfh.write( _data )

    assert dmd5 == mfh.md5_hexdigest, \
        (dmd5, mfh.md5_hexdigest)


def test_md5_through_chunk():
    si = make_stream_item('2012-08-08T08:24:23.0Z', 'hi')
    si.body = ContentItem(raw = 'foo' * 100)

    path = '/tmp/foo-%s' % str(uuid.uuid1())
    ch = Chunk(path=path, mode='wb')
    ch.add(si)
    ch.add(si)
    ch.add(si)
    ch.close()

    data = open(path).read()

    assert ch.md5_hexdigest == hashlib.md5(data).hexdigest()
