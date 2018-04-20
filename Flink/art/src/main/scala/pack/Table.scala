package pack

import org.apache.flink.streaming.api.scala._
import org.apache.flink.table.sources.CsvTableSource
//import org.apache.flink.api.scala._
import org.apache.flink.types.Row
import org.apache.flink.streaming.api.TimeCharacteristic
//import org.apache.flink.streaming.api.scala.{DataStream, StreamExecutionEnvironment}
import org.apache.flink.table.api.TableEnvironment
import org.apache.flink.table.sources.CsvTableSource
//import org.apache.flink.api.common.typeinfo.Types
import org.apache.flink.table.api.Types
import org.apache.flink.table.api.scala._

object Table {

  def main(args: Array[String]) : Unit = {

    println("Start CepTest2 ...")

    val env = StreamExecutionEnvironment.getExecutionEnvironment
    env.setStreamTimeCharacteristic(TimeCharacteristic.EventTime)
    val tableEnv = TableEnvironment.getTableEnvironment(env)

    println("Read csv ...")

    val csvtable = CsvTableSource
      .builder
      .path("/home/esa/projects/LA/LogFile/PreProsessed/EX1/Log_EX1_gen_track_5_mod.csv")
      .ignoreFirstLine
      .fieldDelimiter(",")
      .field("time", Types.SQL_TIMESTAMP)
      .field("id", Types.STRING)
      .field("sources", Types.STRING)
      .field("targets", Types.STRING)
      .field("attr", Types.STRING)
      .field("data", Types.STRING)
      .build

    println("csvtable: " + csvtable)
    println("registerTableSource ...")

    tableEnv.registerTableSource("test", csvtable)

    println("tableEnv.scan ...")

    val tableTest = tableEnv
      .scan("test")
      .filter('time > "2018-03-06 10:55:00".toTimestamp)
      .select("time,id,sources,targets,data")

    println("toAppendStream ...")

    val stream = tableEnv.toAppendStream[Row](tableTest)

    println("stream.print ...")

    stream.print()
    //stream.writeAsCsv("/home/esa/projects/LA/LogFile/Log_EX1_gen_track_5_results.csv")

    println("execute ...")

    env.execute()
  }
}


