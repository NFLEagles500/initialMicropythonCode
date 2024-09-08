import rp2
import network
import time
import urequests
import envSecrets
import ubinascii
import machine
import os
import ntptime


def picoOnboardLED():
    #Set onboard LED address
    devCheck = os.uname()
    if 'Pico W' in devCheck.machine:
        dev = 'picow'
        return machine.Pin('LED', machine.Pin.OUT)
    else:
        dev = 'pico'
        return machine.Pin(25, machine.Pin.OUT)

#functions
def utcToLocal(type):
    global localUtcOffset
    global months
    localTime = utime.localtime(utime.time() + localUtcOffset)
    if type == 'time':
        return f'{localTime[3]:02d}:{localTime[4]:02d}:{localTime[5]:02d}'
    elif type == 'date':
        return f'{localTime[0]}-{localTime[1]:02d}-{localTime[2]:02d}'
    else:
        return f'{localTime[0]}/{months[localTime[1]]}/{localTime[2]:02d} {localTime[3]:02d}:{localTime[4]:02d}:{localTime[5]:02d}'
    
def connect():
    #set country code for wifi
    rp2.country('US')
    #Setup WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.config(hostname=envHostname.hostname,pm = 0xa11140)
    wlan.active(True)
    #Getting the MAC address
    macAddress = ubinascii.hexlify(network.WLAN().config('mac'),':').decode()
    wlan.connect(envSecrets.ssid, envSecrets.wifipsw)
     # Wait for connect or fail
    max_wait = 20
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print('waiting for connection...')
        time.sleep(1)
        # Handle connection error
    if wlan.status() != 3:
        raise RuntimeError('network connection failed')
    else:
        print('connected')
        status = wlan.ifconfig()
    print( 'ip = ' + status[0] )
    try:
        ntptime.settime()
        print(f"Current UTC: {machine.RTC().datetime()}")
    except:
        print("Unable to set Network Time Protocol")
