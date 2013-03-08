package test;

import org.apache.thrift.protocol.TBinaryProtocol;
import org.apache.thrift.transport.TFileTransport;
import streamcorpus.StreamItem;

/**
 * User: jacek
 * Date: 3/8/13
 * Time: 3:38 PM
 */
public final class ReadThrift {
    public static void main(String[] args) {
        try {
            TFileTransport transport = new TFileTransport("test-data/john-smith-tagged-by-lingpipe-0.sc", true);
            transport.open();

            TBinaryProtocol protocol = new TBinaryProtocol(transport);
            int counter = 0;
            while (true) {
                final StreamItem item = new StreamItem();
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
