package pack

import org.apache.flink.api.common.functions.MapFunction
import org.apache.flink.api.java.utils.ParameterTool
import org.apache.flink.api.scala.{DataSet, ExecutionEnvironment}
import org.apache.flink.table.api.TableEnvironment
import org.apache.flink.api.scala._
import org.apache.flink.core.fs.FileSystem.WriteMode
import org.apache.flink.table.sinks.{CsvTableSink, TableSink}
import org.apache.flink.table.sources.CsvTableSource

object BatchTable {

  //class MyMap extends MapFunction[(Int, Int), (String, Int, Int)]{
  //  def map(value: (Int, Int)): (String, Int, Int) = {
  //    return ("foo", value._2 / 2, value._1)
  //  }
  //}

  def main(args: Array[String]) : Unit = {

    val params: ParameterTool = ParameterTool.fromArgs(args)

    println("Start BatchTable ...")

    //val env = ExecutionEnvironment.createLocalEnvironment()
    val env = ExecutionEnvironment.getExecutionEnvironment

    val lines:DataSet[(String,String,String,String,String,String)] =
    //val lines:DataSet[(Array[String])] =
      env.readTextFile("/home/esa/projects/LA/LogFile/PreProsessed/EX1/Log_EX1_gen_track_6.csv")
        .map(line => {
          val fieldsArray = line.split(",")
          (fieldsArray(0), fieldsArray(1), fieldsArray(2), fieldsArray(3), fieldsArray(4), fieldsArray(5)) })

    val lines2 = env.readTextFile("/home/esa/projects/LA/LogFile/PreProsessed/EX1/Log_EX1_gen_track_1.csv")

    //val csvInput: DataSet[(String,String,String,String,String,String)] = env.readCsvFile[(String,String,String,String,String,String)]("/home/esa/projects/LA/LogFile/PreProsessed/EX1/Log_EX1_gen_track_6.csv",
    val csvInput = env.readCsvFile[(String,String,String,String,String,String)]("/home/esa/projects/LA/LogFile/PreProsessed/EX1/Log_EX1_gen_track_6.csv",
      ignoreFirstLine=false).map{ m => (m._1,m._2,m._3,m._4,m._5,m._6)}


    //val csvInput = env.readCsvFile("/home/esa/projects/LA/LogFile/PreProsessed/EX1/Log_EX1_gen_track_6.csv",
    //  ignoreFirstLine=true)

    println("lines: ")
    lines.print()
    //csvInput.print()

    val tableEnv = TableEnvironment.getTableEnvironment(env)

    //val csvSource = new CsvTableSource("/home/esa/projects/LA/LogFile/PreProsessed/EX1/Log_EX1_gen_track_6.csv")
    //tableEnv.registerTableSource("CsvTable",csvSource)

    //tableEnv.registerDataSet("mytable",csvInput,'time,'id,'sources,'targets,'attr,'data)
    tableEnv.registerDataSet("mytable",csvInput)

    //val result = tableEnv.sqlQuery("SELECT * FROM mytable")
    val result = tableEnv.sqlQuery(
      """
        |SELECT *
        |FROM mytable
      """.stripMargin)

    println("result: " + result.toString())
    //result.printSchema()

    //val sink = new CsvTableSink("/home/esa/projects/results/result.csv",fieldDelim=",")
    //result.writeToSink(sink)

    if (params.has("output")) {
      csvInput.writeAsCsv(params.get("output"), "\n", " ")
      env.execute("Scala BatchTable")
    } else {
      println("csvInput: ")
      csvInput.print()
      println("lines2: ")
      lines2.print()

      csvInput.writeAsCsv("file:///home/esa/projects/results/csvinput_test.csv", "\n", ",", WriteMode.OVERWRITE)
      lines2.writeAsText("file:///home/esa/projects/results/lines2_test.csv", WriteMode.OVERWRITE)
      env.execute("Scala BatchTable")

    }

    //env.execute()
  }
}


