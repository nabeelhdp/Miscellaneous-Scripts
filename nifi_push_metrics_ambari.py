#!/usr/bin/python

import subprocess
import sys
import urllib2
from urllib2 import URLError
import socket
import re
import json
import time
import ConfigParser
import getpass
import optparse
import string
import os
import urllib
import ssl
from ConfigParser import SafeConfigParser

def get_config_params():
  # If config file explicitly passed, use it. Else fall back to config.ini as default filename
  config_file = sys.argv[1] if len(sys.argv) >= 2 else os.path.join(os.path.dirname(__file__),"config.ini")
  config_dict = {}
  try:
    with open(config_file) as f:
      try:
        parser = SafeConfigParser()
        parser.readfp(f)
      except ConfigParser.Error, err:
        print 'Could not parse: %s Exiting', err
        sys.exit(1)
  except IOError as e:
    print "Unable to access %s. Error %s \nExiting" % (config_file, e)
    sys.exit(1)

  # Prepare dictionary object with config variables populated
  config_dict = {}
  config_dict["ams_host"] = parser.get('ambari_metrics_config', 'ams_host')
  config_dict["ams_port"] = parser.get('ambari_metrics_config', 'ams_port')
  config_dict['nifi_host'] = parser.get('nifi_config','host')
  config_dict['nifi_port'] = int(parser.get('nifi_config','port'))
  config_dict["nifi_user"] = parser.get('nifi_config','user')
  config_dict["nifi_password"] = parser.get('nifi_config','password')

  return config_dict

def get_auth_request():
  config_dict = get_config_params()
  data = {}
  data['username'] = config_dict['nifi_user']
  data['password'] = config_dict["nifi_password"]
  url_values = urllib.urlencode(data)
  token_url = "https://%s:%d/nifi-api/access/token" % (config_dict['nifi_host'], config_dict['nifi_port'])
  headers = {'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8'}
  req = urllib2.Request(token_url,url_values,headers=headers)
  return req

def get_auth_token():

  httpHandler = urllib2.HTTPSHandler(context=set_ssl())
  # Set debug levels if needed
  #httpHandler.set_http_debuglevel(1)
  opener = urllib2.build_opener(httpHandler)
  req = get_auth_request()
  try:
    resp = opener.open(req)
    tdata = resp.read()
    token = 'Bearer ' + tdata
    return token
  except (urllib2.URLError, urllib2.HTTPError) as err:
    return 'NiFi authentication failed with error: %s' % err

def get_stats(headers,url,ctx):
  req = urllib2.Request(url,headers=headers)
  resp = urllib2.urlopen(req,context=ctx)
  stats = json.loads(resp.read())
  return stats

def set_ssl():
  # BAD CODE : Ignores SSL - equivalent to cancelling cert prompt.
  context = ssl.create_default_context()
  context.check_hostname = False
  context.verify_mode = ssl.CERT_NONE
  return context

def get_flow_status():
  token = get_auth_token()
  config_dict = get_config_params()
  if token.startswith('Bearer'):
    headers = {'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8','Authorization': token }
    flow_status_url = 'https://%s:%d/nifi-api/flow/status' % (config_dict['nifi_host'], config_dict['nifi_port'])
    flow_status = get_stats(headers, flow_status_url, set_ssl())
    return flow_status['controllerStatus']
  else:
    return "FAIL"

def get_system_diagnostics():
  token = get_auth_token()
  config_dict = get_config_params()
  if token.startswith('Bearer'):
    headers = {'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8','Authorization': token }
    diagnostic_url = 'https://%s:%d/nifi-api/system-diagnostics' % (config_dict['nifi_host'], config_dict['nifi_port'])
    system_diagnostics = get_stats(headers, diagnostic_url, set_ssl())
    return system_diagnostics['systemDiagnostics']['aggregateSnapshot']
  else:
    return "FAIL"

# Publishing the Metrics to Collector
def publish_metrics(metric_data,ams_collector_host,ams_collector_port):

  test_socket(
    ams_collector_host,
    ams_collector_port,
    "AMS Collector"
    )
  # Submit metrics to AMS Collector
  url = "http://{}:{}/ws/v1/timeline/metrics".format(
      str(ams_collector_host),
      str(int(ams_collector_port))
      )
  headers = {
    'Content-type': 'application/json',
    'Accept': 'application/json'
    }
  req = urllib2.Request(
      url,
      metric_data,
      headers
      )
  try:
    response = urllib2.urlopen(
          req,
          timeout=3
          )
    print "Response code was: %d" %response.getcode()
    return 1
  except (urllib2.URLError, urllib2.HTTPError) as e:
    print 'Metrics submission failed with error:', e.errno
    return 0

# Prepare json object for each of the Oozie metrics in format recognized by Ambari metrics
def construct_metric(key,value,hostname,timestamp):
  metrics = {}
  vals = {}
  metric_dict = {}
  metrics["hostname"] = hostname
  metrics["appid"] = "NiFi"
  metrics["type"]="COUNTER"
  metrics["starttime"] = timestamp
  metrics["timestamp"] = timestamp
  metrics["metricname"] = key
  vals[timestamp] = value
  metrics["metrics"] = vals
  # Construct ambari metrics style json object to insert into AMS Collector
  metric_dict ["metrics"] = [metrics]
  metric_json=json.dumps(metric_dict, indent=4, sort_keys=True)
  return metric_json

def main():

  # If config file explicitly passed, use it. Else fall back to zk_config.ini as default filename
  config_file = sys.argv[1] if len(sys.argv) >= 2 else 'config.ini'
  config_dict = {}
  config_dict = get_config_params(config_file)
  ams_collector_timeout = 3
  flowstatus_data = get_flow_status()
  sysdiag_data = get_system_diagnostics()
  # Set a timestamp per iteration as time when we gather the metrics
  timestamp = int(time.time()*1000)

  for metric in ['activeThreadCount','runningCount','stoppedCount','invalidCount','disabledCount']
    key = "nifi_instance_name={}_{}.metric={}".format(
      config_dict['nifi_host'] ,
      config_dict['nifi_port'],
      metric
      )
    value = flowstatus_data[metric]
    metric_data_json = construct_metric(
              str(key),
              value,
              config_dict['nifi_host'],
              timestamp
              )
    counter += publish_metrics(
        metric_data_json,
        config_dict["ams_collector_host"],
        config_dict["ams_collector_port"]
        )

  for metric in ['usedHeapBytes','maxHeapBytes','availableProcessors','totalThreads','daemonThreads'] :
    key = "nifi_instance_name={}_{}.metric={}".format(
      config_dict['nifi_host'] ,
      config_dict['nifi_port'],
      metric
      )
    value = sysdiag_data[metric]
    metric_data_json = construct_metric(
              str(key),
              value,
              config_dict['nifi_host'],
              timestamp
              )
    counter += publish_metrics(
        metric_data_json,
        config_dict["ams_collector_host"],
        config_dict["ams_collector_port"]
        )


if __name__ == "__main__":
  main()
