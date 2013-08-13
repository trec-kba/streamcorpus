package streamcorpus_example

import org.apache.thrift.transport.{TTransportException, TIOStreamTransport, TTransport}
import java.io.{FileOutputStream, FileInputStream}
import java.nio.ByteBuffer
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
    var si_count = 0
    i_transport.open()
    while (true) {
      try {
	// deserialize the StreamItem from input transport
        val item: StreamItem = StreamItem.decode(i_protocol)
	si_count += 1
        item.body match {
          case Some(contentItem) => {

	    // taggings is optional
            contentItem.taggings + 
	      ("my_tagger" -> Some(Tagging(
	        taggerId = "my_tagger",
                rawTagging = ByteBuffer.wrap(Array[Byte]()),  // serialized tagging data in some "native" format, such as XML or JSON
	        taggerConfig = Option("some description"),
                taggerVersion = Option("v0.0.infinity"),
                generationTime = Some(StreamTime(zuluTimestamp="1970-01-01T00:00:01.000000Z", epochTicks=1))
              )));

            contentItem.sentences +
	      "my_tagger" -> Seq(Sentence(tokens = Seq(
	          Token(0, "The"), 
		  Token(1, "cat", entityType = Some(EntityType.Per), mentionType = Some(MentionType.Nom), mentionId=1),
		  Token(2, "ate"),
		  Token(3, "the"),
		  Token(4, "bird", entityType = Some(EntityType.Per), mentionType = Some(MentionType.Nom), mentionId=2),
		  Token(5, ".")  // a tagger can define whatever tokenization and sentence chunking it likes
              )));

            //contentItem.relations + ("my_tagger" -> Seq(Relation(

	    println(contentItem.sentences)
	    println(contentItem.sentences.contains("my_tagger"))

          }
          case None => println("no content")
        }
	// serialize the item to the output transport
        item.write(o_protocol)
      } catch {
        case te: TTransportException => if (te.getType == TTransportException.END_OF_FILE) {
          i_transport.close()
          o_transport.close()
          println("FINISHED writing " + si_count + " StreamItems")
          return
        } else {
          println("type " + te.getType)
        }
      }
    }
  }
}
