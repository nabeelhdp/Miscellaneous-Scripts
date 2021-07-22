import subprocess
import sys

from pyspark import SparkContext
from pyspark.sql import HiveContext
from functools import reduce
from pyspark.sql import DataFrame

tablename=sys.argv[1]
args = "hdfs dfs -ls -R "+tablename+" | grep orc$ |awk '{print $NF}'"
proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
tbl_output, s_err = proc.communicate()
all_orc_files = tbl_output.split()

sc = SparkContext()
hiveCtx = HiveContext(sc)

dfs = []

for orc_file in all_orc_files:
    curr_df = hiveCtx.read.format("orc").option("basePath", tablename).load(orc_file)
    dfs.append(curr_df)
    #final_df = final_df.union(curr_df)
    print(dfs[-1].count())

final_df = reduce(DataFrame.union,dfs)
print("Final df has %d" % ( final_df.count()))
print(final_df.head())
final_df.repartition(1).write.partitionBy("biz_dt","biz_status").orc("/tmp/merge_table")
#df.repartition(1).write.partitionBy("biz_dt","biz_status").orc("/data/SI/SG/SI_DCMS_TB_FIN_TRANSACTION_MERGED")
