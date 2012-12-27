
## import the thrift library
from thrift import Thrift
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

from cStringIO import StringIO

from .ttypes import StreamItem, ContentItem, Label, StreamTime, Offset, Rating, Annotator

class Chunk(object):
    '''
    A serialized batch of StreamItem instances.
    '''
    def __init__(self, data=None, file_obj=None):
        '''
        Load a chunk from an existing file handle or buffer of data.
        If no data is passed in, then chunk starts as empty and
        chunk.add(stream_item) can be called to append to it.
        '''
        self._count = 0
        self._o_chunk_fh = None
        self._o_protocol = None
        self._o_transport = None
        if data is None and file_obj is None:
            ## Make output file obj for thrift, wrap in protocol
            self._o_transport = StringIO()
            self._o_protocol = TBinaryProtocol.TBinaryProtocol(self._o_transport)

        elif file_obj is not None and 'w' in file_obj.mode:
            ## use the file object for writing out the data as it
            ## happens, i.e. in streaming mode.
            self._o_chunk_fh = file_obj            
            self._o_transport = TTransport.TBufferedTransport(self._o_chunk_fh)
            self._o_protocol = TBinaryProtocol.TBinaryProtocol(self._o_transport)
            ## this causes _i_chunk_fh to be None below
            file_obj = None

        elif file_obj is None:
            ## wrap it in a file obj
            file_obj = StringIO(data)
            file_obj.seek(0)

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
            self._o_chunk_fh.close()

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
