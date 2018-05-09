package pack

import org.apache.flink.api.common.functions.MapFunction
import org.apache.flink.api.java.utils.ParameterTool
import org.apache.flink.api.scala.{DataSet, ExecutionEnvironment}
import org.apache.flink.table.api.TableEnvironment

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
      env.readTextFile("/home/esa/projects/LA/LogFile/PreProsessed/EX1/Log_EX1_gen_track_6.csv")
        .map(m => m.split(","))

    val lines2 = env.readTextFile("/home/esa/projects/LA/LogFile/PreProsessed/EX1/Log_EX1_gen_track_1.csv")
    //val csvInput = env.readCsvFile[(String,String,String,String,String,String)]("/home/esa/projects/LA/LogFile/PreProsessed/EX1/Log_EX1_gen_track_6.csv",
    //  ignoreFirstLine=true)
    //val csvInput = env.readCsvFile("/home/esa/projects/LA/LogFile/PreProsessed/EX1/Log_EX1_gen_track_6.csv",
    //  ignoreFirstLine=true)

    //lines.print()

    val tableEnv = TableEnvironment.getTableEnvironment(env)

    tableEnv.registerDataSet("mytable",lines)
    val result = tableEnv.sqlQuery("SELECT .... FROM myTable ....")

    if (params.has("output")) {
      lines.writeAsCsv(params.get("output"), "\n", " ")
      env.execute("Scala WordCount Example")
    } else {
      println("lines: ")
      lines.print()
      println("lines2: ")
      lines2.print()
    }

    //env.execute()
  }
}


