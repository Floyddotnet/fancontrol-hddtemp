#!/usr/bin/python3 -u
import sys
import subprocess
import os
import time
import signal
import datetime

def signal_handler(signal, frame):  fn_exit()

def fn_exit():
    os.remove(PIDFILE)
    
    print("\nprogram exiting gracefully")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

INTERVALL = 1 #seconds
DISKS = "ls /dev/sd[a-z]"

PIDFILE="/var/run/fancontrol-hddtemp.pid"
LOCATION = "/var/lib/fancontrol-hddtemp"
FILE_MAX = LOCATION + "/fancontrol-hddtemp-maximum"
FILE_AVG = LOCATION + "/fancontrol-hddtemp-average"
FILE_DAT = LOCATION + "/fancontrol-hddtemp-lastupdate"

if not os.path.exists(LOCATION):
    os.makedirs(LOCATION)

if os.path.exists(PIDFILE):
    print("File " + PIDFILE + " exists, is fancontrol-hddtemp already running?")
    sys.exit(0)
    
with open(PIDFILE, "w") as f: f.write(str(os.getpid()))
    
while True:
    MAX_TEMP = 0
    SUM_TEMP = 0
    AVG_TEMP = 0
    COUNT_TEMP = 0
        
    lsdisks = subprocess.getoutput(DISKS).splitlines()
    for disk in lsdisks:
        tempOut=subprocess.getoutput("smartctl --attributes " + disk + " | grep -E '^19[04]' | tail -1 | tr -s ' ' | cut -d ' ' -f 10")   

        #print(disk + ":" + tempOut)        
        
        temp = int(tempOut)
        
        MAX_TEMP = max(MAX_TEMP, int(temp))
        SUM_TEMP += temp
        COUNT_TEMP += 1
    
    AVG_TEMP = int(SUM_TEMP / COUNT_TEMP)
    
    with open(FILE_MAX, "w") as f: f.write(str(MAX_TEMP*1000))
    with open(FILE_AVG, "w") as f: f.write(str(AVG_TEMP*1000))
    with open(FILE_DAT, "w") as f: f.write(str(datetime.datetime.now().isoformat()))
    
    time.sleep( INTERVALL )
    
fn_exit()    
    
