package test;

import org.apache.thrift.protocol.TBinaryProtocol;
import org.apache.thrift.transport.TIOStreamTransport;
import org.apache.thrift.transport.TTransport;
import streamcorpus.StreamItem;

import java.io.BufferedInputStream;
import java.io.FileInputStream;

/**
 * User: jacek
 * Date: 3/8/13
 * Time: 3:38 PM
 */
public final class ReadThrift {
    public static void main(String[] args) {
        try {
            // File transport magically doesn't work
//            TTransport transport = new TFileTransport("test-data/john-smith-tagged-by-lingpipe-0.sc", true);
            TTransport transport = new TIOStreamTransport(new BufferedInputStream(new FileInputStream("test-data/john-smith-tagged-by-lingpipe-0.sc")));
            TBinaryProtocol protocol = new TBinaryProtocol(transport);
            transport.open();
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
