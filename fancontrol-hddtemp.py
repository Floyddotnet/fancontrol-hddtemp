#!/usr/bin/python3 -u
import sys
import subprocess
import os
import time
import signal
import datetime
import atexit

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

FAN = "/sys/devices/platform/it87.2608/hwmon/hwmon2/pwm2"
FAN_MIN_PWM=100
FAN_MAX_PWM=255
FAN_MIN_TEMP=30
FAN_MAX_TEMP=40

_FAN_PWM_PER_C = (FAN_MAX_PWM-FAN_MIN_PWM) / (FAN_MAX_TEMP-FAN_MIN_TEMP)
print ("Config FAN_PWM_PER_C: " + str(_FAN_PWM_PER_C))

#utils
def fn_write_file(file,content):
    with open(file, "w") as f: 
        f.write(str(content))

def fn_write_pidfile():
    if not os.path.exists(LOCATION):
        os.makedirs(LOCATION)
    
    if os.path.exists(PIDFILE):
        print("File " + PIDFILE + " exists, is fancontrol-hddtemp already running?")
        sys.exit(0)
        
    fn_write_file(PIDFILE, os.getpid())

#singnal handler
def signal_handler(signal, frame):  
    fn_exit()

@atexit.register
def fn_exit():
    set_fanpwmcontrol(False)
    
    if os.path.exists(PIDFILE):
        os.remove(PIDFILE)
            
        print("\nprogram exiting gracefully")
        sys.exit(0)

signal.signal(signal.SIGABRT, signal_handler)
signal.signal(signal.SIGINT,  signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

#impl
def fn_temps():
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
    
    fn_write_file(FILE_HDD_MAX, MAX_HDD_TEMP*1000)
    fn_write_file(FILE_HDD_AVG, AVG_HDD_TEMP*1000)
    fn_write_file(FILE_LASTUPDATE, datetime.datetime.now().isoformat())
    
    #GET CPU-TEMP
    #CPU-Temp is used for better air-flow in chassis if hdd's are idle but cpu under heavy load
    cpuTemp = 0
    with open(SENSOR_CPU_TEMP, "r") as f: cpuTemp = int(int(f.read())/1000)

    SENSOR_TEMP = MAX_HDD_TEMP

    if SENSOR_CPU_MIN_TEMP <= cpuTemp:
        SENSOR_TEMP = max(MAX_HDD_TEMP, cpuTemp)

    fn_write_file(FILE_SENSOR, SENSOR_TEMP*1000)
        
    return int(SENSOR_TEMP);

def set_fanpwmcontrol(enable):
    fn_write_file(FAN + "_enable", "1" if enable else "0")
        
def set_fanspeed(temp):
    pwm = FAN_MIN_PWM
    
    if temp > FAN_MIN_TEMP:
        pwm = min(255,min(FAN_MAX_PWM, FAN_MIN_PWM + ((temp-FAN_MIN_TEMP) * _FAN_PWM_PER_C) ))
    
    pwm = int(max(FAN_MIN_PWM, pwm))
    
    fn_write_file(FAN, pwm)
    #print (temp, str(pwm), _FAN_PWM_PER_C)

try:
    fn_write_pidfile()
    
    while True:
        set_fanpwmcontrol(True)
        
        temp = fn_temps()
        set_fanspeed(temp)
    
        time.sleep( INTERVALL )
finally:
    fn_exit()    
    
