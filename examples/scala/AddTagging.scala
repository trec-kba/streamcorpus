import java.io.FileInputStream
import org.apache.thrift.protocol.TBinaryProtocol
import org.apache.thrift.transport.{TTransportException, TIOStreamTransport, TTransport}
import streamcorpus.{StreamItem}

object Test {
  def main(args: Array[String]) {
    val transport: TTransport = new TIOStreamTransport(new FileInputStream("../test-data/john-smith-tagged-by-lingpipe-0.sc"))
    val binProto: TBinaryProtocol = new TBinaryProtocol(transport)
    transport.open()
    while (true) {
      try {
        StreamItem.decode(binProto).body match {
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