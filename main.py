#If you are using a Pico W, be sure to create the envSecrets.py with hostname, ssid,
#wifipsw, timeApiUrl. timeApiUrl is:
# 'https://timeapi.io/api/TimeZone/zone?timeZone={INSERT TIME ZONE HERE}'

from machine import Pin, UART, RTC
from utime import sleep, sleep_ms, time, localtime
import network
import envSecrets
import ntptime
import usys
import uos

#Setting defaults depending on which pico
devCheck = uos.uname()
if 'Pico W' in devCheck.machine:
    dev = 'picow'
    led = Pin('LED', Pin.OUT)
else:
    dev = 'pico'
    led = Pin(25, Pin.OUT)
led.value(0)

def utcToLocal(type):
    #get the offset from timeapi.io, using your timezone
    response = urequests.get(envSecrets.timeApiUrl)
    localUtcOffset = response.json()['currentUtcOffset']['seconds']
    localTime = localtime(time() + localUtcOffset)
    if type == 'time':
        return f'{localTime[3]:02d}:{localTime[4]:02d}:{localTime[5]:02d}'
    elif type == 'date':
        return f'{localTime[0]}/{localTime[1]}/{localTime[2]:02d}'
    else:
        return f'{localTime[0]}/{localTime[1]}/{localTime[2]:02d} {localTime[3]:02d}:{localTime[4]:02d}:{localTime[5]:02d}'

def connect():
    #Connect to WLAN
    while wlan.isconnected() == False:
        wlan.disconnect()
        #Be sure to set {hostname} below
        wlan.active(True)
        wlan.connect(envSecrets.ssid, envSecrets.wifipsw)
        while wlan.isconnected() == False:
            print('Waiting for connection...')
            sleep(1)
        print(wlan.ifconfig())

if dev == 'picow':
    wlan = network.WLAN(network.STA_IF)
    wlan.disconnect()
    connect()
    try:
        ntptime.settime()
        print(f"{utcToLocal('datetime')}")
    except Exception as error:
        print(error)
        pass

#Start coding.  Blink added for example
while True:
    led.toggle()
    sleep(1)

        
