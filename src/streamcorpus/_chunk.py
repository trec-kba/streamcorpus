
## import the thrift library
from thrift import Thrift
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

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
        self._o_protocol = None
        self._o_transport = None
        if data is None and file_obj is None:
            ## Make output file obj for thrift, wrap in protocol
            self._o_transport = StringIO()
            self._o_protocol = TBinaryProtocol.TBinaryProtocol(self._o_transport)

        elif file_obj is None:
            ## wrap it in a file obj
            file_obj = StringIO(data)
            file_obj.seek(0)

        ## set _chunk_fh, possibly to None
        self._chunk_fh = file_obj

    def add(self, stream_item):
        'add stream_item object to chunk'
        assert self._o_protocol, 'cannot add to a Chunk instantiated with data'
        stream_item.write(self._o_protocol)
        self._count += 1

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
        assert self._chunk_fh, 'cannot iterate over stream_items in an empty Chunk'
        ## seek to the start, so can iterate multiple times over the chunk
        self._chunk_fh.seek(0)
        ## wrap the file handle in buffered transport
        i_transport = TTransport.TBufferedTransport(self._chunk_fh)
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
