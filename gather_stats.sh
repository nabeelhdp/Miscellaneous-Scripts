LOCATION="/tmp"
# Per disk stats
iostat -dmx | awk  '!/Linux|Device/{now=strftime("%Y-%m-%d %H:%M:%S "); if(NF>1){print now $0}}' >> $LOCATION/iostat.txt
# Per CPU stats
mpstat -P ALL | awk  '!/Linux|CPU/{now=strftime("%Y-%m-%d "); if(NF>1){print now $0}}'  >> $LOCATION/mpstat.txt
# Swap check and blocked processes
vmstat | awk  '{now=strftime("%Y-%m-%d %H:%M:%S "); print now $0}' >> $LOCATION/vmstat.txt
# Check for socket accumulation
netstat -pten | awk  '{now=strftime("%Y-%m-%d %H:%M:%S "); print now $0}' >> $LOCATION/netstat.txt
