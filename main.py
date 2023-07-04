from machine import Pin, UART, RTC
import utime
import time
import network
import secrets
import os
import ntptime
import sys
import uos

#Setting onboard LED depending on Pico type
devCheck = os.uname()
if 'Pico W' in devCheck.machine:
    led = Pin('LED', Pin.OUT)
else:
    led = Pin(25, Pin.OUT)
led.value(0)

while True:
  led.toggle()
  sleep(1)
