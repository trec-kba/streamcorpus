import java.io.FileInputStream
import org.apache.thrift.protocol.TBinaryProtocol
import org.apache.thrift.transport.{TIOStreamTransport, TTransport, TFileTransport}
import streamcorpus.StreamItem

/**
 * Date: 3/7/13
 * Time: 12:31 PM
 */

object Test {
  def main(args: Array[String]) {
    val transport: TTransport = new TIOStreamTransport(new FileInputStream("test-data/john-smith-tagged-by-lingpipe-0.sc"))
    val binProto: TBinaryProtocol = new TBinaryProtocol(transport)
    transport.open()
    println(binProto)
    while (true) {
      val imm5: StreamItem.Immutable = StreamItem.decode(binProto)
      println(imm5)

    }
  }
}