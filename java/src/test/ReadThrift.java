package test;

import org.apache.thrift.TBase;
import org.apache.thrift.TException;
import org.apache.thrift.protocol.TBinaryProtocol;
import org.apache.thrift.protocol.TProtocol;
import org.apache.thrift.transport.TFileTransport;
import streamcorpus.StreamItem;

import java.io.IOException;

/**
 * User: jacek
 * Date: 3/8/13
 * Time: 3:38 PM
 */
public final class ReadThrift {
    /**
     * Used to create empty objects that will be initialized with values from the file.
     */
    protected final TBaseCreator creator;

    public ReadThrift(final TBaseCreator creator) {
        this.creator = creator;
    }

    public static interface TBaseCreator {
        TBase create();
    }

    /**
     * Reads the next object from the file.
     */
    public TBase read(TProtocol binaryIn) throws IOException {
        TBase t = creator.create();
        try {
            t.read(binaryIn);
        } catch (TException e) {
            throw new IOException(e);
        }
        return t;
    }

    public static void main(String[] args) {

        ReadThrift readThrift = new ReadThrift(new TBaseCreator() {
            @Override
            public TBase create() {
                return new StreamItem();
            }
        });

        try {
            TFileTransport transport = new TFileTransport("test-data/john-smith-tagged-by-lingpipe-0.sc", true);
            TBinaryProtocol protocol = new TBinaryProtocol(transport);
            transport.open();
            int counter = 0;
            while (true) {
                StreamItem item = new StreamItem();
                item.read(protocol);
                System.out.println("counter = " + ++counter);
                System.out.println("item = " + item);
                if (item == null) {
                    break;
                }
            }
            transport.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
