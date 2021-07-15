#I’ve seen a common use case where we need to search for timegaps in logs where the process goes “silent”. For e.g. GC pauses happening, but no GC logging enabled etc. Or CPU starvation for any other reason etc. The following awk lines may be helpful to spot a timeline gap in the log
awk 'BEGIN{ threshold=177} /^20[0-9][0-9]/{ if(!length(curr_time)){ split($1, d, "-") ; split($2, t, ":") ; curr_time = mktime(d[1] " " d[2] " " d[3] " " t[1] " " t[2] " " t[3]); curr_line=$0 } else{ split($1, d, "-") ;split($2, t, ":"); prev_time = curr_time; prev_line=curr_line ;curr_time = mktime(d[1] " " d[2] " " d[3] " " t[1] " " t[2] " " t[3]); curr_line=$0 ; gap = curr_time-prev_time; if(gap > threshold) { printf "=====Line %d =========================================================================\n", NR; print prev_line; print " | " ; printf " %d seconds gap\n",gap ; print " | " ; print curr_line ; flag=1 } } } END { if(flag!=1){print "No pauses found in log"}}'   <filename>
#Sample: (No pauses found more than threshold defined)
[nmoidu@HW15016 HaaS_Jan_2018]$ awk ' /^20[0-9][0-9]/{ if(!length(curr_time)){ split($1, d, "-") ; split($2, t, ":") ; curr_time = mktime(d[1] " " d[2] " " d[3] " " t[1] " " t[2] " " t[3]); curr_line=$0 } else{ split($1, d, "-") ;split($2, t, ":"); prev_time = curr_time; prev_line=curr_line ;curr_time = mktime(d[1] " " d[2] " " d[3] " " t[1] " " t[2] " " t[3]); curr_line=$0 ; gap = curr_time-prev_time; if(gap > 178) { printf "=====Line %d =========================================================================\n", NR; print prev_line; print " | " ; printf " %d seconds gap\n",gap ; print " | " ; print curr_line ; flag=1 } } } END { if(flag!=1){print "No pauses found in log"}}' hiveserver2.log.node12
# No pauses found in log
#Sample ( Pauses found above threshold)
[nmoidu@HW15016 HaaS_Jan_2018]$ awk ' /^20[0-9][0-9]/{ if(!length(curr_time)){ split($1, d, "-") ; split($2, t, ":") ; curr_time = mktime(d[1] " " d[2] " " d[3] " " t[1] " " t[2] " " t[3]); curr_line=$0 } else{ split($1, d, "-") ;split($2, t, ":"); prev_time = curr_time; prev_line=curr_line ;curr_time = mktime(d[1] " " d[2] " " d[3] " " t[1] " " t[2] " " t[3]); curr_line=$0 ; gap = curr_time-prev_time; if(gap > 177) { printf "=====Line %d =========================================================================\n", NR; print prev_line; print " | " ; printf " %d seconds gap\n",gap ; print " | " ; print curr_line ; flag=1 } } } END { if(flag!=1){print "No pauses found in log"}}' hiveserver2.log.node12
#=====Line 265383 =========================================================================
#
#2018-01-29 23:09:51,560 INFO  [FusionCommonDestroyExecutor]: client.ReplicatedFC (ReplicatedFC.java:destroy(757)) - Closing instance: 801421498
#|
#178 seconds gap
#|
#2018-01-29 23:12:49,333 INFO  [HiveServer2-Handler-Pool: Thread-19699]: thrift.ThriftCLIService (ThriftCLIService.java:OpenSession(294)) - Client protocol version: HIVE_CLI_SERVICE_PROTOCOL_V8
#=====Line 265623 =========================================================================

#2018-01-29 23:54:51,823 INFO  [FusionCommonDestroyExecutor]: client.ReplicatedFC (ReplicatedFC.java:destroy(757)) - Closing instance: 268290953
#|
#178 seconds gap
|#
#2018-01-29 23:57:49,045 INFO  [HiveServer2-Handler-Pool: Thread-19917]: thrift.ThriftCLIService (ThriftCLIService.java:OpenSession(294)) - Client protocol version: HIVE_CLI_SERVICE_PROTOCOL_V8
