
package pack

import pack.datatypes.TestData
import pack.sources.TestDataSource
import org.apache.flink.api.java.utils.ParameterTool
import org.apache.flink.streaming.api.TimeCharacteristic
import org.apache.flink.streaming.api.scala.StreamExecutionEnvironment
import org.apache.flink.streaming.api.windowing.time.Time
import org.apache.flink.cep.scala.{CEP, PatternStream}
import org.apache.flink.cep.scala.pattern.Pattern
import org.apache.flink.cep.{PatternFlatSelectFunction, PatternFlatTimeoutFunction}
import org.apache.flink.streaming.api.datastream.SingleOutputStreamOperator
import org.apache.flink.util.Collector
import org.apache.flink.streaming.api.scala._

import scala.collection.Map


object CepIPP {
  def main(args: Array[String]) {

    println("CepTestData is starting ...")
    val params = ParameterTool.fromArgs(args)
    val input = params.getRequired("input")

    val speed = 600   // events of 10 minutes are served in 1 second

    // set up the execution environment
    val env = StreamExecutionEnvironment.getExecutionEnvironment
    // operate in Event-time
    env.setStreamTimeCharacteristic(TimeCharacteristic.EventTime)

    // get the taxi ride data stream, in order
    val events = env.addSource(new TestDataSource(input, speed))

    println("CepTestData pattern ...")

    // A complete taxi ride has a START event followed by an END event
    val eventPattern = Pattern
      .begin[TestData]("start").where(_.eventIdStr.equals("5.1"))
      .followedBy("end").where(_.eventIdStr.equals("5.4"))

      .within(Time.minutes(5))

    println("CepTestData pattern stream ...")

    // We want to find rides that have NOT been completed within 120 minutes
    val pattern: PatternStream[TestData] = CEP.pattern[TestData](events, eventPattern)


    // side output tag for rides that time out
    val timedoutTag = new OutputTag[TestData]("timedout")

    // collect rides that timeout
    val timeoutFunction = (map: Map[String, Iterable[TestData]], timestamp: Long, out: Collector[TestData]) => {
      val rideStarted = map.get("start").get.head
      out.collect(rideStarted)
    }

    // ignore rides that complete on time
    val selectFunction = (map: Map[String, Iterable[TestData]], collector: Collector[TestData]) => {
        val startEvent = map.get("start").get.head
        val endEvent = map.get("end").get.head

        collector.collect(startEvent)
        collector.collect(endEvent)
        println("Start: eventIdStr: " + startEvent.eventIdStr)
        println("Start: sources: " + startEvent.sources)
    }

    println("CepTestData select ...")

    val longRides = pattern.flatSelect(selectFunction)

    longRides.print()

    println("CepTestData execute ...")

    env.execute("CEP Test Data")
  }
}
