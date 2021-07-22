from pyspark import SparkContext 
from pyspark import SparkConf
from pyspark.sql import HiveContext
from pyspark.sql.functions import col
import sys


conf = SparkConf().setAppName("merge").set("spark.sql.orc.filterPushdown","true")
sc = SparkContext(conf=conf)
hc = HiveContext(sc)
tablepath = sys.argv[1]
filepath = ""
if len(sys.argv) > 1:
  filepath = sys.argv[2]
else:
  filepath = sys.argv[1]
merged_tablepath = tablepath + "_MERGED"
df = hc.read.format("orc").option("basePath",tablepath).load(filepath).filter(col("partition_col")=="val1")
df.repartition(1).write.partitionBy("partition_col1","partition_col2").orc(merged_tablepath)

