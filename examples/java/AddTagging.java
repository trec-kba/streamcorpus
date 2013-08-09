
import org.apache.thrift.protocol.TBinaryProtocol;
import org.apache.thrift.transport.TIOStreamTransport;
import org.apache.thrift.transport.TTransport;
import org.apache.thrift.transport.TTransportException;
import streamcorpus.EntityType;
import streamcorpus.Sentence;
import streamcorpus.StreamItem;
import streamcorpus.Token;

import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.util.ArrayList;

/**
 * User: jacek
 * Date: 3/8/13
 * Time: 3:38 PM
 */
public final class AddTagging {
    public static void main(String[] args) {
        try {
            TTransport i_transport = new TIOStreamTransport(new BufferedInputStream(new FileInputStream("test-data/john-smith-tagged-by-lingpipe-0-v0_3_0.sc")));
            TTransport o_transport = new TIOStreamTransport(new BufferedOutputStream(new FileOutputStream("test-data/john-smith-tagged-by-lingpipe-0-v0_3_0-augmented.sc")));
            try {
                TBinaryProtocol i_protocol = new TBinaryProtocol(i_transport);
                TBinaryProtocol o_protocol = new TBinaryProtocol(o_transport);
                i_transport.open();
                int counter = 0;
                while (true) {
                    final StreamItem item = new StreamItem();
                    item.read(i_protocol);
                    System.out.println("counter = " + ++counter);
                    System.out.println("item = " + item);

                    ArrayList<Sentence> sentences = new ArrayList<Sentence>();
                    ArrayList<Token> tokens = new ArrayList<Token>();


                    Token tok = new Token(0, "The");
                    tok.equiv_id = 2;
                    tok.entity_type = EntityType.FAC;

                    tokens.add(tok);

                    tokens.add(new Token(1, "cat"));
                    tokens.add(new Token(2, "jumped"));
                    tokens.add(new Token(3, "high"));

                    Sentence sentence = new Sentence(tokens);


                    sentences.add(sentence);
                    item.body.sentences.put("my_tagger", sentences);
                    item.write(o_protocol);
                }


            } catch (TTransportException te) {
                if (te.getType() == TTransportException.END_OF_FILE) {
                    System.out.println("*** EOF ***");
                    i_transport.close();
                    o_transport.close();
                }
            }
        } catch (Exception e1) {


        }
    }
}
