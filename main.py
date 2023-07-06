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
import urequests

def update_main_script():
    response = urequests.get(github_url)
    new_code = response.text
    response.close()

    # Check if the new code is different from the existing code
    if new_code != open('main.py').read():
        # Save the new main.py file
        with open('main.py', 'w') as f:
            f.write(new_code)

        # Reset the Pico to apply the updated main.py
        machine.reset()

#Setting defaults depending on which pico
devCheck = uos.uname()
if 'Pico W' in devCheck.machine:
    dev = 'picow'
    led = Pin('LED', Pin.OUT)
else:
    dev = 'pico'
    led = Pin(25, Pin.OUT)
led.value(0)

def appLog(stringOfData):
    with open('log.txt','a') as file:
        file.write(f"{utcToLocal('datetime')} {stringOfData}\n")
    print(f"{utcToLocal('datetime')} {stringOfData}")

def utcToLocal(type):
    #get the offset from timeapi.io, using your timezone
    localTime = localtime(time() + localUtcOffset)
    if type == 'time':
        return f'{localTime[3]:02d}:{localTime[4]:02d}:{localTime[5]:02d}'
    elif type == 'date':
        return f'{localTime[0]}/{localTime[1]}/{localTime[2]:02d}'
    else:
        return f'{localTime[0]}/{localTime[1]}/{localTime[2]:02d} {localTime[3]:02d}:{localTime[4]:02d}:{localTime[5]:02d}'

wlan = network.WLAN(network.STA_IF)
wlan.disconnect()

def connect():
    #Connect to WLAN
    while wlan.isconnected() == False:
        wlan.config(hostname='picotest')
        wlan.active(True)
        wlan.connect(envSecrets.ssid, envSecrets.wifipsw)
        iter = 1
        while wlan.isconnected() == False:
            print(f'Not Connected...{iter}')
            iter += 1
            if iter == 10:
                print('Reached max waiting for wifi')
                break
            sleep(1)
        ip = wlan.ifconfig()[0]
        print(f'{network.hostname()} is connected on {ip}')

#Variables
#If you need the output as your script runs, add appLog('String of data') throughout the script.
#When you change verbose to True, appLog will send the data to a log.txt for you to evaluate after
#execution and it will print to the console as well
verbose = False
# URL of the raw main.py file on GitHub
github_url = 'https://raw.githubusercontent.com/NFLEagles500/initialMicropythonCode/main/main.py'

if dev == 'picow':
    wlan = network.WLAN(network.STA_IF)
    connect()
    # Perform initial update on startup
    update_main_script()
    try:
        ntptime.settime()
        print(f"{utcToLocal('datetime')}")
        responseFromTimeapi = urequests.get(envSecrets.timeApiUrl)
        localUtcOffset = responseFromTimeapi.json()['currentUtcOffset']['seconds']
    except Exception as error:
        appLog(error)
        pass

#Start coding.  Blink added for example
while True:
    led.toggle()
    sleep(0.02)

        
