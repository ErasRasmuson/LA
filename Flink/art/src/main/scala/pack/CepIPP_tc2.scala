
package pack

import org.apache.flink.api.java.utils.ParameterTool
import org.apache.flink.cep.scala.pattern.Pattern
import org.apache.flink.cep.scala.{CEP, PatternStream}
import org.apache.flink.streaming.api.TimeCharacteristic
import org.apache.flink.streaming.api.scala.{StreamExecutionEnvironment, _}
import org.apache.flink.streaming.api.windowing.time.Time
import org.apache.flink.util.Collector
import pack.datatypes.TestData
import pack.sources.TestDataSource

import scala.collection.Map
//import org.apache.flink.cep.scala.conditions


object CepIPP_tc2 {
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

    //val keyedEvents = events.keyBy(_.eventId)

    println("CepTestData pattern ...")
    val eventPattern = Pattern
      .begin[TestData]("start").where(_.eventIdStr.equals("0.0"))
      .followedBy("middle").where(
        (value,ctx) => {
          // Does not work yet !!
          println("map: " + ctx.getEventsForPattern("middle").map(_.eventIdStr).foreach(println))
          lazy val sum = ctx.getEventsForPattern("middle").map(_.eventIdStr.length).sum
          println("sum: " + sum)
          //value.eventIdStr.startsWith("0") && sum > 0
          sum > 0
      })
      .within(Time.minutes(5))

    println("CepTestData pattern stream ...")

    //val pattern: PatternStream[TestData] = CEP.pattern[TestData](keyedEvents, eventPattern)
    val pattern: PatternStream[TestData] = CEP.pattern[TestData](events, eventPattern)

    val timedoutTag = new OutputTag[TestData]("timedout")

    val timeoutFunction = (map: Map[String, Iterable[TestData]], timestamp: Long, out: Collector[TestData]) => {
      val rideStarted = map.get("start").get.head
      out.collect(rideStarted)
    }

    val selectFunction = (map: Map[String, Iterable[TestData]], collector: Collector[TestData]) => {
        val startEvent = map.get("start").get.head
        val endEvent = map.get("end").get.head

        collector.collect(startEvent)
        collector.collect(endEvent)
        println("Start: eventIdStr: " + startEvent.eventIdStr + " Time: " + startEvent.eventTime)
        println("End  : eventIdStr: " + endEvent.eventIdStr + " Time: " + endEvent.eventTime)
    }

    println("CepTestData select ...")

    val longRides = pattern.flatSelect(selectFunction)

    longRides.print()

    println("CepTestData execute ...")

    env.execute("CEP TC2 Test Data")
  }
}
