package streamcorpus_example

import org.apache.thrift.transport.{TTransportException, TIOStreamTransport, TTransport}
import java.io.{FileOutputStream, FileInputStream}
import org.apache.thrift.protocol.TBinaryProtocol
import streamcorpus._

/**
 * User: jacek
 * Date: 8/10/13
 * Time: 3:20 PM
 */

object AddTagging {
  def main(args: Array[String]) {
    val i_transport: TTransport = new TIOStreamTransport(new FileInputStream("../../test-data/john-smith-tagged-by-lingpipe-0-v0_3_0.sc"))
    val o_transport: TTransport = new TIOStreamTransport(new FileOutputStream("/tmp/john-smith-tagged-by-lingpipe-0-v0_3_0.sc"))
    val i_protocol: TBinaryProtocol = new TBinaryProtocol(i_transport)
    val o_protocol: TBinaryProtocol = new TBinaryProtocol(o_transport)
    val count: Int = 0
    i_transport.open()
    while (true) {
      try {
	// deserialize the StreamItem from input transport
        val item: StreamItem = StreamItem.decode(i_protocol);
	count = count + 1;
        item.body match {
          case Some(contentItem) => {
            contentItem.sentences + ("my_tagger" -> Seq(Sentence(Seq(Token(0, "The"), Token(1, "cat", entityType = Some(EntityType.Per))))))
          }
          case None => println("no content")
        }
	// serialize the item to the output transport
        item.write(o_protocol)
      } catch {
        case te: TTransportException => if (te.getType == TTransportException.END_OF_FILE) {
          i_transport.close()
          o_transport.close()
          println("FINISHED writing " + count + " StreamItems")
          return
        } else {
          println("type " + te.getType)
        }
      }
    }
  }
}
