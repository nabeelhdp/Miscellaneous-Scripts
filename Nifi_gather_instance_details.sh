!/bin/bash

NIFI_API_URL="http://127.0.0.1:9092/nifi-api"

echo "======================================================"
echo "Limits:"
ulimit -a
echo "======================================================"
echo "Hostname:"
hostname -f
echo "======================================================"
echo "CPU Info:"
dmidecode -t4 |awk '/Populated/ {print $2}'|wc -l
cat /proc/cpuinfo | grep 'vendor' | uniq
cat /proc/cpuinfo | grep 'model name' | uniq
cat /proc/cpuinfo | grep processor | wc -l
echo "======================================================"
echo "sysctl output:"
sysctl -a
echo "======================================================"
echo "Release version:"
cat /proc/version
echo "======================================================"
echo "Memory details:"
cat /proc/meminfo
echo "======================================================"
echo "Disk Space Utilization:"
df -mh
echo "======================================================"
echo "Network Interface information:"
ifconfig
for i in $(ifconfig | grep "^[a-z]" | cut -f 1 -d " "); 
  do echo -e "$i\n-------------------------" ; 
  ethtool $i; 
  ethtool -k $i; 
  ethtool -S $i; 
  ethtool -i $i;
  echo -e "\n" ; 
  done
echo "======================================================"
echo "Contents of nifi.properties file: "
cat /usr/hdf/current/nifi/conf/nifi.properties
echo "======================================================"
echo "Contents of bootstrap.conf file: "
cat /usr/hdf/current/nifi/conf/bootstrap.conf


echo "======================================================"
echo "Process groups in root: "
curl ${NIFI_API_URL}/flow/process-groups/root/status?recursive=true
echo "======================================================"
echo "NiFi cluster version: "
curl ${NIFI_API_URL}/flow/about
echo "======================================================"
echo "Resources in NiFi cluster: "
curl ${NIFI_API_URL}/resources
echo "======================================================"
echo "NiFi cluster summary: "
curl ${NIFI_API_URL}/flow/cluster/summary
echo "======================================================"
echo "NiFi cluster stats: "
curl${NIFI_API_URL}/flow/status
echo "======================================================"
echo "NiFi cluster processor types: "
curl${NIFI_API_URL}/flow/processor-types
