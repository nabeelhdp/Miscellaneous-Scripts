# Scrapes JMX output for RM UI
# http://<RM-HOST>:8088/jmx?qry=Hadoop:service=ResourceManager,name=QueueMetrics,q0=root
#
# Look at the following metrics:
#
#    "AllocatedContainers" : 0,
#    "AggregateContainersAllocated" : 0,
#    "AggregateNodeLocalContainersAllocated" : 0,
#    "AggregateRackLocalContainersAllocated" : 0,
#    "AggregateOffSwitchContainersAllocated" : 0,
#
# Compute the metrics for aggregate percentage of job localization achieved in the cluster. 
# Sort the metric by queue, print and write same output to a csv file
 
import json
import sys 
import csv

util_level={}

outfile = './LocalUtilization.csv'
writefile = sys.open(outfile,'at')
writer=csv.writer(writefile)

with open('jmx-response.json') as jmxfile:
  stats=json.load(jmxfile)
  for k,v in stats.iteritems():
    for jmx_vals in v:
      try:
        if int(jmx_vals['AggregateContainersAllocated']) > 0 :
          node_local_percentage = float(jmx_vals['AggregateNodeLocalContainersAllocated'])*100/float(jmx_vals['AggregateContainersAllocated'])
          util_level[jmx_vals['tag.Queue']] = round(node_local_percentage,2)
          total_containers_allocated[jmx_vals['tag.Queue']] = jmx_vals['AggregateContainersAllocated']
      except KeyError,e:
        pass
    print("===============================")
    print("| Rack Local %  |  Queue Name |")
    print("===============================")
    sorted_d = sorted(util_level.items(), key=lambda (k,v): v)
    try:
        for myitems in sorted_d:
          print("{} \t\t {}".format(myitems[1],myitems[0]))
          writer.writerow((myitems[0],total_containers_allocated[myitems[0]],myitems[1]))
    finally:
        writefile.close()
    print("===============================")

