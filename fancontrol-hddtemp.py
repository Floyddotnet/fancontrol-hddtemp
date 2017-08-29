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

INTERVALL = 10 #seconds
DISKS = "ls /dev/sd[a-z]"

PIDFILE="/var/run/fancontrol-hddtemp.pid"
LOCATION = "/var/lib/fancontrol-hddtemp"
FILE_HDD_MAX = LOCATION + "/fancontrol-hddtemp-hdd-maximum"
FILE_HDD_AVG = LOCATION + "/fancontrol-hddtemp-hdd-average"
FILE_LASTUPDATE = LOCATION + "/fancontrol-hddtemp-lastupdate"
FILE_SENSOR = LOCATION + "/fancontrol-hddtemp-temp-sensor"

SENSOR_CPU_TEMP = "/sys/devices/platform/coretemp.0/hwmon/hwmon1/temp1_input"
SENSOR_CPU_MIN_TEMP = 45 #ignore CPU-sensor if lower than this value

if not os.path.exists(LOCATION):
    os.makedirs(LOCATION)

if os.path.exists(PIDFILE):
    print("File " + PIDFILE + " exists, is fancontrol-hddtemp already running?")
    sys.exit(0)
    
with open(PIDFILE, "w") as f: f.write(str(os.getpid()))
    
while True:
    MAX_HDD_TEMP = 0
    SUM_HDD_TEMP = 0
    AVG_HDD_TEMP = 0
    COUNT_HDD_TEMP = 0
        
    lsdisks = subprocess.getoutput(DISKS).splitlines()
    for disk in lsdisks:
        tempOut=subprocess.getoutput("smartctl --attributes " + disk + " | grep -E '^19[04]' | tail -1 | tr -s ' ' | cut -d ' ' -f 10")   

        #print(disk + ":" + tempOut)        
        
        temp = int(tempOut)
        
        MAX_HDD_TEMP = max(MAX_HDD_TEMP, int(temp))
        SUM_HDD_TEMP += temp
        COUNT_HDD_TEMP += 1
    
    AVG_HDD_TEMP = int(SUM_HDD_TEMP / COUNT_HDD_TEMP)
    
    with open(FILE_HDD_MAX, "w") as f: f.write(str(MAX_HDD_TEMP*1000))
    with open(FILE_HDD_AVG, "w") as f: f.write(str(AVG_HDD_TEMP*1000))
    with open(FILE_LASTUPDATE, "w") as f: f.write(str(datetime.datetime.now().isoformat()))
    
    #GET CPU-TEMP
    #CPU-Temp is used for better air-flow in chassis if hdd's are idle but cpu under heavy load
    cpuTemp = 0
    with open(SENSOR_CPU_TEMP, "r") as f: cpuTemp = int(int(f.read())/1000)

    SENSOR_TEMP = MAX_HDD_TEMP

    if SENSOR_CPU_MIN_TEMP <= cpuTemp:
        SENSOR_TEMP = max(MAX_HDD_TEMP, cpuTemp)

    with open(FILE_SENSOR, "w") as f: f.write(str(SENSOR_TEMP*1000))


    time.sleep( INTERVALL )
    
fn_exit()    
    
