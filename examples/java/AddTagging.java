
import org.apache.thrift.protocol.TBinaryProtocol;
import org.apache.thrift.transport.TIOStreamTransport;
import org.apache.thrift.transport.TTransport;
import org.apache.thrift.transport.TTransportException;
import streamcorpus.EntityType;
import streamcorpus.Sentence;
import streamcorpus.StreamItem;
import streamcorpus.Token;

import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.util.Arrays;

/**
 * User: jacek
 * Date: 3/8/13
 * Time: 3:38 PM
 */
public final class AddTagging {
    public static void main(String[] args) {
        try {
            final TTransport i_transport = new TIOStreamTransport(new FileInputStream("test-data/john-smith-tagged-by-lingpipe-0-v0_3_0.sc"));
            final TTransport o_transport = new TIOStreamTransport(new FileOutputStream("test-data/john-smith-tagged-by-lingpipe-0-v0_3_0-augmented.sc"));
            try {
                final TBinaryProtocol i_protocol = new TBinaryProtocol(i_transport);
                final TBinaryProtocol o_protocol = new TBinaryProtocol(o_transport);
                i_transport.open();
                int counter = 0;
                while (true) {
                    final StreamItem item = new StreamItem();
                    item.read(i_protocol);
                    System.out.println("counter = " + ++counter);
                    System.out.println("item = " + item);
                    System.out.println("item.body.clean_visible.length " + item.body.clean_visible.length());

                    item.body.sentences.put("my_tagger", Arrays.asList(sentence(tok(0, "The"), tok(1, "cat"), tok(2, "jumped"), tok(3, "high"))));
                    item.write(o_protocol);
                }
            } catch (TTransportException te) {
                if (te.getType() == TTransportException.END_OF_FILE) {
                    System.out.println("*** EOF ***");
                    i_transport.close();
                    o_transport.close();
                } else {
                    throw te;
                }
            }
        } catch (Exception e1) {
            System.err.println(e1);
        }
    }

    // auxiliary functions to make Sentence creation less verbose
    // bringing Java code closer to the spirit of Scala

    static Token tok(int num, String content) {
        final Token tok = new Token(num, content);
        tok.equiv_id = 2;
        tok.entity_type = EntityType.FAC;
        return tok;
    }

    static Sentence sentence(Token... tokens) {
        return new Sentence(Arrays.asList(tokens));
    }
}
