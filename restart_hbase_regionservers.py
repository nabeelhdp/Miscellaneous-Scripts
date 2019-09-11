#!/usr/bin/python

import subprocess
import os
import sys
import urllib2
from urllib2 import URLError
import socket
import re
import base64
import json
import time
import ConfigParser
from ConfigParser import SafeConfigParser
from pprint import pprint


def get_config_params(config_file):
  try:
    with open(config_file) as f:
      try:
        parser = SafeConfigParser()
        parser.readfp(f)
      except ConfigParser.Error, err:
        print 'Could not parse: %s ', err
        return False
  except IOError as e:
    print "Unable to access %s. Error %s \nExiting" % (config_file, e)
    sys.exit(1)

  ambari_server_host = parser.get('ambari_config', 'ambari_server_host')
  ambari_server_port = parser.get('ambari_config', 'ambari_server_port')
  ambari_user = parser.get('ambari_config', 'ambari_user')
  ambari_pass = parser.get('ambari_config', 'ambari_pass')
  ambari_server_timeout = parser.get('ambari_config', 'ambari_server_timeout')
  cluster_name = parser.get('ambari_config', 'cluster_name')

  if not ambari_server_port.isdigit():
    print "Invalid port specified for Ambari Server. Exiting"
    sys.exit(1)
  if not is_valid_hostname(ambari_server_host):
    print "Invalid hostname provided for Ambari Server. Exiting"
    sys.exit(1)
  if not ambari_server_timeout.isdigit():
    print "Invalid timeout value specified for Ambari Server. Using default of 30 seconds"
    ambari_server_timeout = 30

  # Prepare dictionary object with config variables populated
  config_dict = {}
  config_dict["ambari_server_host"] = ambari_server_host
  config_dict["ambari_server_port"] = ambari_server_port
  config_dict["ambari_server_timeout"] = ambari_server_timeout

  if re.match(r'^[A-Za-z0-9_]+$', cluster_name):
    config_dict["cluster_name"] = cluster_name
  else:
    print "Invalid Cluster name provided. Cluster name should have only alphanumeric characters and underscore. Exiting"
    return False

  if re.match(r'^[a-zA-Z0-9_.-]+$', ambari_user):
    config_dict["ambari_user"] = ambari_user
  else:
    print "Invalid Username provided. Exiting"
    return False

  config_dict["ambari_pass"] = ambari_pass

  return config_dict

def is_valid_hostname(hostname):
    if hostname == "":
        return False
    if len(hostname) > 255:
        return False
    if hostname[-1] == ".":
        hostname = hostname[:-1] # strip exactly one dot from the right, if present
    allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
    return all(allowed.match(x) for x in hostname.split("."))

def test_socket(socket_host,socket_port,service_name):
  # Test socket connectivity to requested service port
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
      s.connect((socket_host,int(socket_port)))
    except Exception as e:
      print("Unable to connect to %s host %s:%d. Exception is %s\nExiting!" % (service_name, socket_host,int(socket_port),e))
      sys.exit(1)
    finally:
      s.close()

# Gather state of HBase Regionserver from Ambari
def get_regionserver_state(config_dict,hbregionhost):
    # Test socket connectivity to Oozie server port
    test_socket(config_dict["ambari_server_host"],config_dict["ambari_server_port"],"Ambari server")

    # Construct URL request for metrics data. This needs to be changed when moving to JMX
    url = "http://{}:{}/api/v1/clusters/{}/hosts/{}/host_components/HBASE_REGIONSERVER".format(
            str(config_dict["ambari_server_host"]) ,
            str(int(config_dict["ambari_server_port"])),
            config_dict["cluster_name"],
            hbregionhost
            )
    req = urllib2.Request(url)
    data = ''
    try:
          response = urllib2.urlopen(req,timeout=timeout)
          data = json.loads(response.read())
          hb_regionstate={}
          hb_regionstate['desired_state'] = data['HostRoles']['desired_state']
          hb_regionstate['state'] = data['HostRoles']['state']
          return hb_regionstate
    except (urllib2.URLError, urllib2.HTTPError) as e:
      print 'HBase Region Server status check failed with error:', e.errno


# Submit new Capacity Scheduler config to from Ambari server
def restart_service(restart_request,hbregionhost,config_dict):

    # Construct URL request for metrics data. This needs to be changed when moving to JMX
    url = "http://{}:{}/api/v1/clusters/{}/hosts/{}/host_components/HBASE_REGIONSERVER".format(
            str(config_dict["ambari_server_host"]) ,
            str(int(config_dict["ambari_server_port"])),
            config_dict["cluster_name"],
            hbregionhost
            )
    auth_string = "%s:%s" % (
        config_dict['ambari_user'],
        config_dict['ambari_pass']
        )
    auth_encoded = 'Basic %s' % base64.b64encode(auth_string).strip()
    json_len = len(restart_request)
    req = urllib2.Request(url,data=restart_request)
    req.get_method = lambda: 'PUT'
    req.add_header('Content-Length', json_len )
    req.add_header('Content-Type','application/json')
    req.add_header('Accept','application/json')
    req.add_header('Authorization', auth_encoded)

    httpHandler = urllib2.HTTPHandler()
    httpHandler.set_http_debuglevel(1)
    opener = urllib2.build_opener(httpHandler)

    try:
      response = opener.open(req,timeout=ambari_server_timeout)
      print "Response code was: %d" %response.getcode()
    except (urllib2.URLError, urllib2.HTTPError) as e:
      print 'Restart request failed with error:', e
    except TypeError as e:
      print('Invalid format for submission data %s ' % e)

def main():

  regionserver_list = [
      'server1',
      'server2'  
      ]

  config_file = os.path.join(os.path.dirname(__file__),"ambari_config.ini")
  ambari_config_dict = {}
  ambari_config_dict = get_config_params(config_file)
  hbase_state={}
  restart_request = {
        "HostRoles":
            {
            "state": "STARTED"
            }
        }
  for rs in regionserver_list:
      hbase_state[rs]=get_regionserver_state(config_dict,rs)
      if hbase_state[rs]['desired_state'] == 'STARTED':
          if hbase_state[rs]['desired_state'] != 'STARTED':
              restart_service(json.dumps(restart_request),
                hbregionhost,
                config_dict
                )

if __name__ == "__main__":
  main()
