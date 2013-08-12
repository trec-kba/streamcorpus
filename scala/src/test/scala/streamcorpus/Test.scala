import java.io.{FileOutputStream, FileInputStream}
import org.apache.thrift.protocol.TBinaryProtocol
import org.apache.thrift.transport.{TTransportException, TIOStreamTransport, TTransport}
import streamcorpus.StreamItem

object Test {
  def main(args: Array[String]) {
    val i_transport: TTransport = new TIOStreamTransport(new FileInputStream("../test-data/john-smith-tagged-by-lingpipe-0-v0_3_0.sc"))
    val o_transport: TTransport = new TIOStreamTransport(new FileOutputStream("/tmp/john-smith-tagged-by-lingpipe-0-v0_3_0.sc"))
    val i_binProto: TBinaryProtocol = new TBinaryProtocol(i_transport)
    val o_binProto: TBinaryProtocol = new TBinaryProtocol(o_transport)
    i_transport.open()
    while (true) {
      try {
        StreamItem.decode(i_binProto).body match {
          case Some(contentItem) => {
            for ((k, sentences) <- contentItem.sentences) {
              println(k)
              for (sentence <- sentences; token <- sentence.tokens) {
                println(token.token)
              }
            }
          }
          case _ => println("DUNNO")
        }
        println("--------------------------------------------")
      } catch {
        case te: TTransportException => if (te.getType == TTransportException.END_OF_FILE) {
          println("END")
          return
        } else {
          println("type " + te.getType)
        }
      }
    }
  }
}
