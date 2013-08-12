package test.scala.streamcorpus

import org.apache.thrift.transport.{TTransportException, TIOStreamTransport, TTransport}
import java.io.{FileOutputStream, FileInputStream}
import org.apache.thrift.protocol.TBinaryProtocol
import streamcorpus.{Token, Sentence, StreamItem, EntityType}

/**
 * User: jacek
 * Date: 8/10/13
 * Time: 3:20 PM
 */

object AddTagging {
  def main(args: Array[String]) {
    val i_transport: TTransport = new TIOStreamTransport(new FileInputStream("../../test-data/john-smith-tagged-by-lingpipe-0-v0_3_0.sc"))
    val o_transport: TTransport = new TIOStreamTransport(new FileOutputStream("/tmp/john-smith-tagged-by-lingpipe-0-v0_3_0.sc"))
    val i_binProto: TBinaryProtocol = new TBinaryProtocol(i_transport)
    val o_binProto: TBinaryProtocol = new TBinaryProtocol(o_transport)
    i_transport.open()
    while (true) {
      try {
        val item: StreamItem = StreamItem.decode(i_binProto)
        item.body match {
          case Some(contentItem) => {

	    /* jacek, not sure if this is correct syntax -- can you fix it for me? */
	    val tok1: Token = new Token(0, "The")
	    tok1.token_num = 0

	    val tok2: Token = new  Token(1, "cat")
	    tok1.token_num = 1

	    /* especially this needs to work, see Java example */
	    tok2.entity_type = EntityType.PER
	    
	    val tok3: Token = new  Token(1, "is")
	    tok1.token_num = 2


	    val sentence1: Sentence = new Sentence(Seq(tok1, tok2, tok3))
            contentItem.sentences + ("my_tagger" -> Seq(sentence1))
          }
          case None => println("no content")
        }
        item.write(o_binProto)
      } catch {
        case te: TTransportException => if (te.getType == TTransportException.END_OF_FILE) {
          i_transport.close()
          o_transport.close()
          println("END")
          return
        } else {
          println("type " + te.getType)
        }
      }
    }
  }
}