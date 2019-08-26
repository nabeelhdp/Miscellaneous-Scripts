#!/bin/python
 
import httplib
import json
import yaml
from pprint import pprint
 
h = httplib.HTTPConnection("172.25.33.5:11000")
h.request('GET', '/oozie/v2/admin/metrics')
response = h.getresponse()
print response.status,response.reason
content_length =  response.getheader('Content-Type')
print content_length
 
data = ''
data = response.read()
metric_data = json.loads(data)
 
for key, value in metric_data['counters'].items():
    print(key,value)
 
for k,v in json.load(open('instrumentation.json')).items():
  i=0
  while i < len(k):
    for entries in v:
      metrics_counters = str(k+"."+entries)
      print metric_data[metrics_counters]
    i += 1
