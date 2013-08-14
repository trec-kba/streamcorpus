package streamcorpus_example

import org.apache.thrift.transport.{TTransportException, TIOStreamTransport, TTransport}
import java.io.{FileOutputStream, FileInputStream}
import java.nio.ByteBuffer
import org.apache.thrift.protocol.TBinaryProtocol
import streamcorpus._

/**
 * User: jacek, jrf
 * Date: 8/13/13

This illustrates how to construct new tagging metadata for a document
stored in a streamcorpus flat file, aka "chunk file"

Even though the streamcorpus-v0_3_0.thrift interface definition says
entity_type and mention_id, etc., the Scrooge thrift compiler for
Scala converts these to entityType, mentionId, etc, to be more
Scala-ish.  Not sure what happens with collisions in this re-writing
scheme, but it seems to work for the streamcorpus interfaces, which
are consistent with foo_bar naming for property names and FooBar
naming of class names.  After serializing back to a new chunk file,
the resulting output is in the correct field, i.e. entity_type not
entityType, which doesn't exist in any other language using thrift.
Scrooge also renames things in enums, so EntityType.PER becomes
EntityType.Per and AttributeType.PER_AGE becomes AttributeType.PerAge.
This can take some experimentation to find the right new spelling.

The general flow is this:

  1) get content from StreamItem.body.clean_visible (or clean_html),
  see below

  2) do automatic processing of that text

  3) construct an array of Sentence objects, and add it to the
  StreamItem.body.sentences map using a key that identifies the system
  that constructed the tagging, e.g. "my_tagger".  Each Sentence in
  the list of sentences for your tagger has a .tokens property, which
  is an array of Token objects.  This is the most important interface.
  See ../../if/streamcorpus-v0_3_0.thrift for details.

  4) construct an entry for body.taggings describing this tagger system

  5) if available, construct body.relations and body.attributes

  6) put the updated StreamItem back out to a chunk file
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

            // general StreamItem instances have body.raw,
            // body.clean_html, and body.clean_visible.  The last two
            // are the same byte length and already converted to UTF-8
            val raw = contentItem.raw getOrElse ByteBuffer.wrap(Array[Byte]())
            println(raw.toString().length() + " bytes of raw to process")

            val clean_html = contentItem.cleanHtml getOrElse ""
            println(clean_html.length() + " bytes of clean_html to process")

            // clean_visible is generated from clean_html by replacing
            // all tags with whitespace, to maintain byte and
            // character offsets.
            val clean_visible = contentItem.cleanVisible getOrElse ""
            println(clean_visible.length() + " bytes of clean_visible to process")

            val tag: String = "my_tagger"
            // taggings is optional
            val newTaggings = contentItem.taggings + (
              tag -> Tagging(
                taggerId = tag,
                rawTagging = ByteBuffer.wrap(Array[Byte]()), // serialized tagging data in some "native" format, such as XML or JSON
                taggerConfig = Some("some description"),
                taggerVersion = Some("v0.0.infinity"),
                generationTime = Some(StreamTime(zuluTimestamp = "1970-01-01T00:00:01.000000Z", epochTicks = 1))
              ))

            val newSentences = contentItem.sentences + (
              tag -> Seq(
                Sentence(tokens = Seq(
                  Token(0, "The", sentencePos = 0),
                  Token(1, "ten-year-old", sentencePos = 1),
                  Token(2, "cat",
                    entityType = Some(EntityType.Per),
                    mentionType = Some(MentionType.Nom),
                    sentencePos = 2,
                    mentionId = 1,
                    equivId = 1 // identifier for within-doc coref chain
                  ),
                  Token(3, "ate", sentencePos = 3,
                    // part-of-speech names from
                    // http://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html
                    pos = Some("VBD")),
                  Token(5, "the", sentencePos = 4),
                  Token(6, "bird",
                    entityType = Some(EntityType.Per),
                    mentionType = Some(MentionType.Nom),

                    // a parse tree can be recovered from
                    // this format.  The reason to transform
                    // the parse tree data into the tokens,
                    // is that it makes it easier to convert
                    // these strings and pointers to parents
                    // into features for coref and IR
                    // purposes
                    parentId = 3, // sentencePos of parent in parse tree
                    dependencyPath = Some(""), // grammatical relation label on the path to parent

                    sentencePos = 5,
                    mentionId = 2,
                    equivId = 2
                  ),
                  Token(7, ".") // a tagger can define whatever tokenization and sentence chunking it likes
                )),
                Sentence(tokens = Seq(
                  Token(0, "Bad", sentencePos = 0),
                  Token(1, "kitty",
                    entityType = Some(EntityType.Per),
                    mentionType = Some(MentionType.Nom),
                    sentencePos = 1,
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
              tag -> Seq(
                // a list of triples between mentions with labels
                // from RelationType, which can be expanded by
                // adding more to streamcorpus-v0_3_0.thrift
                Relation(mentionId1 = Some(1), mentionId2 = Some(2), relationType = Some(RelationType.LifeInjure))
              )
              )

            val newAttributes = contentItem.attributes + (
              tag -> Seq(
                Attribute(mentionId = Some(1),
                  attributeType = Some(AttributeType.PerAge),
                  evidence = Some("ten-year-old"))
              )
              )

            // in Scala, the item is immutable, so we must copy it.
            // Hopefully this is not too inefficient.  There may be
            // some other kind of proxying scheme that is better.
            // This could also all be inlined, at the expense of
            // readability and ease of debugging.
            val newItem = item.copy(body = Some(contentItem.copy(
              taggings = newTaggings,
              sentences = newSentences,
              relations = newRelations,
              attributes = newAttributes
            )))

            newItem.body match {
              case Some(contentItem) => {

                // verify that the other sentences data was not destroyed
                assert(contentItem.sentences.contains("lingpipe"), println("sentences lost lingpipe"))
                // and that our tagging info got added
                assert(contentItem.sentences.contains(tag), println("sentences missing my_tagger"))

                // verify similar things about taggings
                assert(contentItem.taggings.contains("lingpipe"), println("taggings lost lingpipe"))
                assert(contentItem.taggings.contains(tag), println("taggings missing my_tagger"))

                // verify that relations has our data, there were not reln from lingpipe
                assert(contentItem.relations.contains(tag), println("relations missing my_tagger"))

                // verify that attributes has our data, there were not reln from lingpipe
                assert(contentItem.attributes.contains(tag), println("attributes missing my_tagger"))

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
