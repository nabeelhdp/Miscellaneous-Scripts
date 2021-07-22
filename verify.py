from pyspark import SparkContext 
from pyspark import SparkConf
from pyspark.sql import HiveContext
from pyspark.sql.functions import col
import sys

conf = SparkConf().setAppName("Verify").set("spark.sql.orc.filterPushdown","true")
sc= SparkContext(conf = conf)
hc = HiveContext(sc)

# Take HDFS path to Hive external table as first argument
tablepath = sys.argv[1]

# Pass HDFS path to table and HDFS path to partition to limit merge activity to particular partition
filepath = ""
if len(sys.argv) > 1:
  filepath = sys.argv[2]
else:
  filepath = sys.argv[1]
  
#hc.read.format("orc").option("basePath","/data/MYTABLE/").load("/data/MYTABLE").filter(col("biz_status")=="expired").count()
print(hc.read.format("orc").option("basePath",tablepath).load(filepath).filter(col("partition_col")=="val1").count())
# pyspark --driver-memory 10G --num-executors 40 --executor-memory 4G
