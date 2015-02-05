import os
import uuid
import time
import errno
import shutil
import pytest
from cStringIO import StringIO
import logging
## utility for tests that configures logging in roughly the same way
## that a program calling bigtree should setup logging
logger = logging.getLogger('streamcorpus')
logger.setLevel( logging.DEBUG )
ch = logging.StreamHandler()
ch.setLevel( logging.DEBUG )
formatter = logging.Formatter('%(asctime)s %(process)d %(levelname)s: %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

## import from inside the local package, i.e. get these things through __init__.py
from . import make_stream_item, ContentItem, Chunk, serialize, deserialize, \
    parse_file_extensions, \
    compress_and_encrypt, decrypt_and_uncompress, \
    compress_and_encrypt_path
from . import VersionMismatchError
from . import Versions
from . import StreamItem_v0_2_0, StreamItem_v0_3_0
from streamcorpus import _chunk
from ._chunk import JsonChunk, PickleChunk
from ._cbor_chunk import CborChunk

try:
    import cbor
except:
    cbor = None

TEST_XZ_PATH = os.path.join(os.path.dirname(__file__), '../../../test-data/john-smith-tagged-by-lingpipe-0-v0_2_0.sc.xz')
TEST_SC_PATH = os.path.join(os.path.dirname(__file__), '../../../test-data/john-smith-tagged-by-lingpipe-0-v0_2_0.sc')

def make_si():
    si = make_stream_item( None, 'http://example.com' )
    si.body = ContentItem(raw='hello!')
    return si

def test_version():
    si = make_si()
    assert si.version == Versions.v0_3_0

def test_v0_2_0():
    for si in Chunk(TEST_SC_PATH, message=StreamItem_v0_2_0):
        assert si.version == Versions.v0_2_0

    with pytest.raises(VersionMismatchError):
        for si in Chunk(TEST_SC_PATH, message=StreamItem_v0_3_0):
            pass

def test_chunk():
    ## write in-memory
    ch = Chunk()
    assert ch.mode == 'wb'
    si = make_si()
    ch.add( si )
    assert len(ch) == 1

@pytest.fixture(scope='function', params=[Chunk, PickleChunk])
def chunk_constructor(request):
    return request.param

def test_chunk_wrapper(chunk_constructor):
    ## write in-memory
    fh = StringIO()
    ch = chunk_constructor(file_obj=fh, write_wrapper=lambda x: x['dog'], mode='wb')
    assert ch.mode == 'wb'
    si = make_si()
    si = dict(dog=si)
    ch.add( si )
    assert len(ch) == 1
    ch.flush()
    blob = fh.getvalue()
    assert blob
    fh = StringIO(blob)
    ch = chunk_constructor(file_obj=fh, read_wrapper=lambda x: dict(dog=x), mode='rb')
    si2 = list(ch)[0]
    assert si2 == si


def test_json_chunk():
    chunk_constructor = JsonChunk
    fh = StringIO()
    ch = chunk_constructor(file_obj=fh, mode='wb')
    assert ch.mode == 'wb'
    si = {
        'abs_url':'http://example.com',
        'body': {
            'raw': 'hello!'
        },
    }
    ch.add( si )
    assert len(ch) == 1
    ch.flush()
    blob = fh.getvalue()
    assert blob
    fh = StringIO(blob)
    ch = chunk_constructor(file_obj=fh, message=lambda x: x, mode='rb')
    si2 = list(ch)[0]
    assert si2 == si


@pytest.mark.skipif('cbor is None')
def test_cbor_chunk():
    chunk_constructor = CborChunk
    fh = StringIO()
    ch = chunk_constructor(file_obj=fh, mode='wb')
    assert ch.mode == 'wb'
    si = {
        'abs_url':'http://example.com',
        'body': {
            'raw': 'hello!'
        },
    }
    ch.add( si )
    assert len(ch) == 1
    ch.flush()
    blob = fh.getvalue()
    assert blob
    fh = StringIO(blob)
    ch = chunk_constructor(file_obj=fh, message=lambda x: x, mode='rb')
    si2 = list(ch)[0]
    assert si2 == si


def test_xz():
    count = 0
    for si in Chunk(TEST_XZ_PATH, message=StreamItem_v0_2_0):
        count += 1
        assert si.body.clean_visible
    assert count == 197

def test_gz():
    count = 0
    test_gz_path = '/tmp/test_gz_path.gz'
    cmd = 'cat %s | xz --decompress | gzip -9 > %s' % (TEST_XZ_PATH, test_gz_path)
    os.system(cmd)
    ## hinted by ".gz"
    for si in Chunk(test_gz_path, message=StreamItem_v0_2_0):
        count += 1
        assert si.body.clean_visible
    assert count == 197
    os.system('rm %s' % test_gz_path)

@pytest.mark.skipif('not _chunk.xz')
def test_xz_write():
    count = 0
    test_xz_path = '/tmp/test_path.xz'
    ## hinted by ".xz"
    o_chunk = Chunk(test_xz_path, mode='wb')
    o_chunk.add(make_si())
    o_chunk.close()
    assert len(list(Chunk(test_xz_path))) == 1
    os.system('rm %s' % test_xz_path)

def test_speed():
    count = 0
    start_time = time.time()
    for si in Chunk(TEST_SC_PATH, message=StreamItem_v0_2_0):
        count += 1
        assert si.body.clean_visible
    elapsed = time.time() - start_time
    rate = float(count) / elapsed
    print '%d in %.3f sec --> %.3f per sec' % (count, elapsed, rate)
    assert count == 197


@pytest.fixture(scope='function')
def path(request, tmpdir):
    path = os.path.join(str(tmpdir), 'test_chunk-%s.sc' % str(uuid.uuid4()))
    def fin():
        if os.path.exists(path):
            os.remove(path)
    request.addfinalizer(fin)
    return path

@pytest.fixture(scope='function')
def path_xz(request):
    path = '/tmp/test_chunk-%s.sc.xz' % str(uuid.uuid4())
    def fin():
        os.remove(path)
    request.addfinalizer(fin)
    return path

def test_chunk_path_write(path):
    ## write to path
    ch = Chunk(path=path, mode='wb')
    si = make_si()
    ch.add( si )
    ch.close()
    assert len(ch) == 1
    print repr(ch)
    assert len(list( Chunk(path=path, mode='rb') )) == 1

def test_chunk_path_append(path):
    ch = Chunk(path=path, mode='wb')
    si = make_si()
    ch.add( si )
    ch.close()
    assert len(ch) == 1
    ## append to path
    ch = Chunk(path=path, mode='ab')
    si = make_si()
    ch.add( si )
    ch.close()
    ## count is only for those added
    assert len(ch) == 1
    print repr(ch)
    assert len(list( Chunk(path=path, mode='rb') )) == 2

@pytest.mark.skipif('not _chunk.xz')
def test_chunk_path_append_xz(path_xz):
    ch = Chunk(path=path_xz, mode='wb')
    si = make_si()
    ch.add( si )
    ch.close()
    assert len(ch) == 1
    ## append to path
    ch = Chunk(path=path_xz, mode='ab')
    si = make_si()
    ch.add( si )
    ch.close()
    ## count is only for those added
    assert len(ch) == 1
    print repr(ch)
    assert len(list( Chunk(path=path_xz, mode='rb') )) == 2

def test_chunk_path_read_1(path):
    ch = Chunk(path=path, mode='wb')
    ch.add( make_si() )
    ch.add( make_si() )
    ch.close()
    assert len(ch) == 2
    ## read from path
    ch = Chunk(path=path, mode='rb')
    assert len(list(ch)) == 2
    ## updated by __iter__
    assert len(ch) == 2
    print repr(ch)

def test_chunk_path_read_version_protection(path):
    ch = Chunk(path=path, mode='wb')
    ch.add( make_si() )
    ch.add( make_si() )
    ch.close()
    assert len(ch) == 2
    ## read from path
    with pytest.raises(VersionMismatchError):
        for si in Chunk(path=path, mode='rb', message=StreamItem_v0_2_0):
            pass

def test_chunk_data_read_2(path):
    ch = Chunk(path=path, mode='wb')
    ch.add( make_si() )
    ch.add( make_si() )
    ch.close()
    assert len(ch) == 2
    ## load from data
    data = open(path).read()
    ch = Chunk(data=data, mode='rb')
    assert len(list(ch)) == 2
    ## updated by __iter__
    assert len(ch) == 2
    print repr(ch)

def test_chunk_data_append(path):
    ch = Chunk(path=path, mode='wb')
    ch.add( make_si() )
    ch.add( make_si() )
    ch.close()
    assert len(ch) == 2
    ## load from data
    data = open(path).read()
    ch = Chunk(data=data, mode='ab')
    si = make_si()
    ch.add( si )
    assert len(ch) == 1
    print repr(ch)

def test_serialize():
    si = make_si()
    blob = serialize(si)
    si2 = deserialize(blob)
    assert si.stream_id == si2.stream_id

def test_noexists_exception():
    with pytest.raises(IOError) as excinfo:
        Chunk('path-that-does-not-exist', mode='rb')
    assert excinfo.value.errno == errno.ENOENT

def test_exists_exception(path):
    ch = Chunk(path=path, mode='wb')
    ch.add( make_si() )
    ch.add( make_si() )
    ch.close()
    with pytest.raises(IOError) as excinfo:
        Chunk(path, mode='wb')
    assert excinfo.value.errno == errno.EEXIST

def test_compress_and_encrypt_path(path):
    ch = Chunk(path=path, mode='wb')
    ch.add( make_si() )
    ch.add( make_si() )
    ch.close()
    originalSize = os.path.getsize(path)
    tmp_dir = os.path.join('/tmp', uuid.uuid4().hex)
    errors, o_path = compress_and_encrypt_path(path, tmp_dir=tmp_dir)
    if errors:
        print '\n'.join(errors)
        raise Exception(errors)
    #assert len(open(o_path).read()) in [240, 244, 248]
    print 'path=%r o_path=%r size=%s' % (path, o_path, os.path.getsize(o_path))
    newSize = os.path.getsize(o_path)
    assert newSize < originalSize
    assert (newSize % 4) == 0

    ## this should go in a "cleanup" method...
    shutil.rmtree(tmp_dir)

def test_with(path):
    with Chunk(path, mode='wb') as ch:
        ch.add(make_si())
        ch.add(make_si())
        ch.add(make_si())
    assert len(list(Chunk(path))) == 3

def test_parse_file_extensions():
    examples = [
        ('dog.sc.gz.gpg', ('sc', 'gz', 'gpg')),
        ('dog.gz.gpg', (None, 'gz', 'gpg')),
        ('dog.gpg', (None, None, 'gpg')),
        ('dog.sc.gz', ('sc', 'gz', None)),
        ('dog.gz', (None, 'gz', None)),
        ('dog', (None, None, None)),
        ('dog.sc', ('sc', None, None)),
        ('dog.xz', (None, 'xz', None)),
        ]
    for ex in examples:
        assert ex[1] == parse_file_extensions(ex[0])

def test_fileobj():
    errors, data = decrypt_and_uncompress(open(TEST_XZ_PATH).read())
    count = 0
    for si in Chunk(file_obj=StringIO(data), message=StreamItem_v0_2_0):
        count += 1
        assert si.body.clean_visible
    assert count == 197

@pytest.mark.parametrize('compression', ['xz', 'gz', 'sz', ''])
def test_compression(compression, path):
    ## analog of pytest.skipif for parametrize:
    if compression and not getattr(_chunk, compression):
        logger.warn('not able to run test_compression(%r) because %r not available',
                    compression, compression)
        return

    ## get some raw data in memory for testing
    errors, rdata = decrypt_and_uncompress(open(TEST_XZ_PATH).read())
    assert not errors

    ## first check it all in memory
    errors, cdata = compress_and_encrypt(rdata, compression=compression)
    assert not errors
    assert (not compression) or (len(cdata) < len(rdata))
    errors, rdata2 = decrypt_and_uncompress(cdata, compression=compression, detect_compression=False)
    assert not errors
    assert rdata2 == rdata

    ## now check for the _path version of compress_and_encrypt...
    fh = open(path, 'wb')
    fh.write(rdata)
    fh.close()
    t_dir = os.path.dirname(path)
    errors, o_path = compress_and_encrypt_path(path, compression=compression, 
                                               tmp_dir=t_dir)
    assert not errors
    cdata = open(o_path).read()
    assert (not compression) or (len(cdata) < len(rdata))
    errors, rdata2 = decrypt_and_uncompress(cdata, compression=compression, detect_compression=False)
    assert not errors
    assert rdata2 == rdata

@pytest.mark.parametrize('compression', ['xz', 'gz', 'sz', ''])
def test_detect_compression(compression, path):
    ## analog of pytest.skipif for parametrize:
    if compression and not getattr(_chunk, compression):
        logger.warn('not able to run test_compression(%r) because %r not available',
                    compression, compression)
        return

    ## get some raw data in memory for testing
    errors, rdata = decrypt_and_uncompress(open(TEST_XZ_PATH).read())
    assert not errors

    ## first check it all in memory
    errors, cdata = compress_and_encrypt(rdata, compression=compression)
    assert not errors
    assert (not compression) or (len(cdata) < len(rdata))
    errors, rdata2 = decrypt_and_uncompress(cdata, compression='auto')
    assert not errors
    assert rdata2 == rdata

    ## now check for the _path version of compress_and_encrypt...
    fh = open(path, 'wb')
    fh.write(rdata)
    fh.close()
    t_dir = os.path.dirname(path)
    errors, o_path = compress_and_encrypt_path(path, compression=compression, 
                                               tmp_dir=t_dir)
    assert not errors
    cdata = open(o_path).read()
    assert (not compression) or (len(cdata) < len(rdata))
    errors, rdata2 = decrypt_and_uncompress(cdata, compression='auto')
    assert not errors
    assert rdata2 == rdata
