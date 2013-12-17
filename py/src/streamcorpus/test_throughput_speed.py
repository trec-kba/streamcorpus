import os
import time

## this is a python thing that makes a byte-buffer look like a filehandle
from cStringIO import StringIO
from streamcorpus.ttypes import StreamItem

## these are the thrift library components for reading and writing
## to/from files and file-like objects, such as wrapped byte buffers
from thrift.transport import TTransport
from thrift.protocol.TBinaryProtocol import TBinaryProtocolAccelerated as protocol


class AugmentedStringIO(object):
    '''
    Adapter around a filehandle that wraps .read and .write so that it
    can construct an md5_hexdigest property
    '''
    def __init__(self, fh):
        self._fh = fh
        if hasattr(fh, 'get_value'):
            self.get_value = fh.get_value
        if hasattr(fh, 'seek'):
            self.seek = fh.seek
        if hasattr(fh, 'mode'):
            self.mode = fh.mode
        if hasattr(fh, 'flush'):
            self.flush = fh.flush
        if hasattr(fh, 'close'):
            self.close = fh.close
        if hasattr(fh, 'read'):
            self.read = fh.read
        if hasattr(fh, 'write'):
            self.write = fh.write

    def readAll(self, sz):
        '''
        This method allows TBinaryProtocolAccelerated to actually function.

        Copied from here
        http://svn.apache.org/repos/asf/hive/trunk/service/lib/py/thrift/transport/TTransport.py
        '''
        buff = ''
        have = 0
        while (have < sz):
            chunk = self.read(sz-have)
            have += len(chunk)
            buff += chunk

            if len(chunk) == 0:
                raise EOFError()

        return buff


def deserialize(filehandle, num_objects=1000):
    '''reads num_objects StreamItem objects out of filehandle and returns them in an array
    '''
    ## gather test data in-memory
    test_objects = []

    ## wrap the file handle in buffered transport
    i_transport = TTransport.TBufferedTransport(filehandle)
    ## use the Thrift Binary Protocol
    i_protocol = protocol(i_transport)

    ## read message instances until input buffer is exhausted
    while len(test_objects) < num_objects:
        ## instantiate a message  instance 
        msg = StreamItem()

        try:
            ## read it from the thrift protocol instance
            msg.read(i_protocol)

            ## gather the fully instantiated object into our test data
            test_objects.append(msg)

        except EOFError:
            break        

    return test_objects


def _test_serialize(test_objects, num_loops=10):
    start_time = time.time()

    for step in range(num_loops):

        ## make in-memory filehandle buffer
        fh = AugmentedStringIO( StringIO() )

        ## wrap the IN-MEMORY buffer thrift transport -- must pick
        ## the right one of these for what we are doing, requires
        ## asking more on Thrift email list
        o_transport = TTransport.TBufferedTransport(fh)

        ## use the Thrift Binary Protocol
        o_protocol = protocol(o_transport)
            
        for obj in test_objects:
            obj.write(o_protocol)

        o_transport.flush()
        
        ## maybe assert something about the size of the output buffer

    assert len(fh._fh.getvalue()) > 0

    elapsed = time.time() - start_time

    count = num_loops * len(test_objects) 

    rate = count / elapsed
    
    print '%d in %.3f seconds --> %.1f serializations per second' % (count, elapsed, rate)

    ## return the in-memory file-like object so we can use it as input to the next test
    return fh

def _test_deserialize(string_of_data, num_loops=10, num_objects=1000):
    start_time = time.time()

    for step in range(num_loops):

        test_buffer = AugmentedStringIO( StringIO( string_of_data ) )

        results = deserialize(test_buffer, num_objects=num_objects)

        assert len(results) > 0, results

    elapsed = time.time() - start_time

    count = num_loops * len(results) 

    rate = count / elapsed
    
    print '%d in %.3f seconds --> %.1f serializations per second' % (count, elapsed, rate)


def test_serialize_deserialize():
    ## first load test data:
    fh = AugmentedStringIO( open(os.path.join(os.path.dirname(__file__), '../../../test-data/john-smith-tagged-by-lingpipe-0-v0_3_0.sc') ))

    ## get it off of disk, so we can run purely in memory
    test_objects = deserialize(fh, num_objects=100)

    ## test speed of serializing
    test_buffer = _test_serialize(test_objects)

    ## get a string of the test data
    string_of_data = test_buffer._fh.getvalue()

    ## test deserializing
    _test_deserialize(string_of_data, num_objects=100)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('input', help='path to test data to load')
    parser.add_argument('--num-objects', type=int, default=100, help='max number of objects to use')
    args = parser.parse_args()

    ## first load test data:
    fh = AugmentedStringIO( open(args.input) )

    ## get it off of disk, so we can run purely in memory
    test_objects = deserialize(fh, num_objects=args.num_objects)

    ## test speed of serializing
    test_buffer = _test_serialize(test_objects)

    ## get a string of the test data
    string_of_data = test_buffer._fh.getvalue()

    ## test deserializing
    _test_deserialize(string_of_data, num_objects=args.num_objects)
