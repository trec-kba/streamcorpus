package streamcorpus_example

import org.apache.thrift.transport.{TTransportException, TIOStreamTransport, TTransport}
import java.io.{FileOutputStream, FileInputStream}
import java.nio.ByteBuffer
import org.apache.thrift.protocol.TBinaryProtocol
import streamcorpus._

/**
 * User: jacek, jrf
 * Date: 8/13/13
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
            val newTaggings = contentItem.taggings + (
                "my_tagger" -> Tagging(
                    taggerId = "my_tagger",
                    rawTagging = ByteBuffer.wrap(Array[Byte]()), // serialized tagging data in some "native" format, such as XML or JSON
                    taggerConfig = Option("some description"),
                    taggerVersion = Option("v0.0.infinity"),
                    generationTime = Some(StreamTime(zuluTimestamp = "1970-01-01T00:00:01.000000Z", epochTicks = 1))
                ))

            // Even though the streamcorpus-v0_3_0.thrift interface
            // definition says entity_type and mention_id, etc. the
            // Scrooge thrift compiler for Scala converts these to
            // "entityType" to be more Scala-ish.  Not sure what
            // happens with collisions in this re-writing scheme, but
            // it seems to work for the streamcorpus interfaces, which
            // are consistent with foo_bar naming for property names
            // and FooBar naming of class names.  The resulting output
            // is in the correct field, i.e. entity_type.  Scrooge
            // also renames things in enums, so EntityType.PER becomes
            // EntityType.Per.  This can take some experimentation to
            // find the right spelling.
            val newSentences = contentItem.sentences + (
                "my_tagger" -> Seq(
                    Sentence(tokens = Seq(
                        Token(0, "The"),
                        Token(1, "ten-year-old"),
                        Token(2, "cat", 
                              entityType = Some(EntityType.Per), 
                              mentionType = Some(MentionType.Nom), 
                              mentionId = 1,
                              equivId = 1 // identifier for within-doc coref chain
                          ),
                        Token(3, "ate"),
                        Token(5, "the"),
                        Token(6, "bird", 
                              entityType = Some(EntityType.Per), 
                              mentionType = Some(MentionType.Nom), 
                              mentionId = 2,
                              equivId = 2
                          ),
                        Token(7, ".") // a tagger can define whatever tokenization and sentence chunking it likes
                    )),
                    Sentence(tokens = Seq(
                        Token(0, "Bad"),
                        Token(1, "kitty", entityType = Some(EntityType.Per), 
                              mentionType = Some(MentionType.Nom), 
                              mentionId = 3,
                              equivId = 1 // identifier for within-doc coref chain (see above)
                          ),
                        Token(3, ".")
                    )
                )
            ))

	    // relations and attributes are defined by reference to
	    // mentionId on tokens, which are unique at the document
	    // level
            val newRelations = contentItem.relations + (
              "my_tagger" -> Seq(
                  // a list of triples between mentions with labels
                  // from RelationType, which can be expanded by
                  // adding more to streamcorpus-v0_3_0.thrift
		  Relation(mentionId1 = Option(1), mentionId2 = Option(2), relationType = Option(RelationType.LifeInjure))
                )
              )

            val newAttributes = contentItem.attributes + (
              "my_tagger" -> Seq(
		 Attribute(mentionId = Option(1), attributeType = Option(AttributeType.PerAge), evidence = Option("ten-year-old"))
	      )
            )

            val newItem = item.copy(body = Some(contentItem.copy(
              taggings = newTaggings,
              sentences = newSentences,
              relations = newRelations,
	      attributes = newAttributes
            )))

            newItem.body match {
              case Some(contentItem) => {

	        // verify that the other sentences data was not destroyed
                assert (contentItem.sentences.contains("lingpipe"), println("sentences lost lingpipe"))
		// and that our tagging info got added
                assert (contentItem.sentences.contains("my_tagger"), println("sentences missing my_tagger"))

	        // verify similar things about taggings
                assert (contentItem.taggings.contains("lingpipe"), println("taggings lost lingpipe"))
                assert (contentItem.taggings.contains("my_tagger"), println("taggings missing my_tagger"))

		// verify that relations has our data, there were not reln from lingpipe
                assert (contentItem.relations.contains("my_tagger"), println("relations missing my_tagger"))

		// verify that attributes has our data, there were not reln from lingpipe
                assert (contentItem.attributes.contains("my_tagger"), println("attributes missing my_tagger"))

                println("valid")

              }
              case _ =>
            }

            newItem.write(o_protocol)
          }
          case None => {
            println("no content")
            item.write(o_protocol)
          }
        }
        // serialize the item to the output transport
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
