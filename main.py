'''
Must be used on QTpy ESP32 Pico
References:
    https://learn.adafruit.com/adafruit-qt-py-esp32-pico/overview
    For esp32 only micropython machine.deepsleep and machine.lightsleep:
    https://www.engineersgarage.com/micropython-esp32-modem-light-deep-sleep-modes-timer-external-touch-wake-up/#:~:text=There%20are%20two%20external%20%E2%80%9Cwake,of%20its%20capacitive%20touch%20pins.
    https://docs.micropython.org/en/latest/esp32/quickref.html
'''
import utime
import uos
import machine
from neopixel import NeoPixel
import esp32

def utcToLocal(type):
    #get the offset from timeapi.io, using your timezone
    global localUtcOffset
    localTime = utime.localtime(utime.time() + localUtcOffset)
    if type == 'time':
        return f'{localTime[3]:02d}:{localTime[4]:02d}:{localTime[5]:02d}'
    elif type == 'date':
        return f'{localTime[0]}/{localTime[1]}/{localTime[2]:02d}'
    else:
        return f'{localTime[0]}/{localTime[1]}/{localTime[2]:02d} {localTime[3]:02d}:{localTime[4]:02d}:{localTime[5]:02d}'

def connect():
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(envSecrets.ssid, envSecrets.wifipsw)
    iter = 1
    while wlan.ifconfig()[0] == '0.0.0.0':
        print(f'Not Connected...{iter}')
        iter += 1
        utime.sleep(1)
        if iter == 10:
            wlan.connect(envSecrets.ssid, envSecrets.wifipsw)
            iter = 1
    ip = wlan.ifconfig()[0]
    print(f'{network.hostname()} is connected on {ip}')

def tone(pin,frequency,duration):
    pin.freq(frequency)
    pin.duty_u16(30000)
    utime.sleep_ms(duration)
    pin.duty_u16(0)

resetCauseNames = ['PWRON_RESET','HARD_RESET','WDT_RESET','DEEPSLEEP_RESET','SOFT_RESET','BROWN_OUT_RESET']
wakeReasons = ['PIN_WAKE','EXT0_WAKE','EXT1_WAKE','TIMER_WAKE','TOUCHPAD_WAKE','ULP_WAKE']
resetCause = next(item for item in resetCauseNames if machine.reset_cause() == getattr(machine, item))

power_pin = machine.Pin(8, machine.Pin.OUT)  # NeoPixel power is on pin 8
power_pin.on()  # Enable the NeoPixel Power
batt_adc_power = machine.Pin(33, machine.Pin.OUT)
#esp32 ADC setup
battery_adc = machine.ADC(32)
battery_adc.atten(machine.ADC.ATTN_11DB)
interrupt_pin = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_DOWN)
pin = machine.Pin(5, machine.Pin.OUT)  # Onboard NeoPixel is on pin 5
np = NeoPixel(pin, 1)  # create NeoPixel driver on pin 5 for 1 pixel

#print(f'Reset Cause: {machine.reset_cause()} Wake Reason: {machine.wake_reason()}')
blink_iter = 1
while blink_iter > 0:
    np.fill((0, 0, 150))  # Set the NeoPixel blue
    np.write()  # Write data to the NeoPixel
    utime.sleep(0.5)  # Pause for 0.5 seconds
#    np.fill((0, 0, 0))  # Turn the NeoPixel off
#    np.write()  # Write data to the NeoPixel
    utime.sleep(0.5)  # Pause for 0.5 seconds
    blink_iter = blink_iter - 1
#deepsleep will NOT process interrupts, it will only restart the microcontroller
#interrupt_pin.irq(trigger=Pin.IRQ_RISING, handler=wake_up)

resistor_1 = 10000  # Resistor 1 value in ohms
resistor_2 = 5000  # Resistor 2 value in ohms
voltage_warn = 4.4  # Warning voltage level in volts
adc_warn = 29300
oneVolt = 1162
#oneVolt = 1137.5 # this is the correct calculation

#actual_voltage = (readVoltage / oneVolt) * (resistor_1 + resistor_2) / resistor_2

batt_adc_power.value(1)
utime.sleep(1)
actual_voltage = (battery_adc.read() / oneVolt) * (resistor_1 + resistor_2) / resistor_2
if resetCause == 'DEEPSLEEP_RESET':
    wakeReason = next(item for item in wakeReasons if machine.wake_reason() == getattr(machine, item))
    currDateTime = f'{utime.localtime()[0]}/{utime.localtime()[1]}/{utime.localtime()[2]} {utime.localtime()[3] - 7:02d}:{utime.localtime()[4]:02d}:{utime.localtime()[5]:02d}'
    with open('log.txt','a') as file:
        file.write(f'{currDateTime} Reset Cause: {resetCause} Wake Reason: {wakeReason} Battery voltage: {actual_voltage:.2f}\n')
    
    print(f'{currDateTime} Reset Cause: {resetCause} Wake Reason: {wakeReason} Battery voltage: {actual_voltage:.2f}')
else:
    import network
    import envSecrets
    import ntptime
    import urequests
    wlan = network.WLAN(network.STA_IF)
    connect()
    ntptime.settime()
    responseFromTimeapi = urequests.get(envSecrets.timeApiUrl)
    localUtcOffset = responseFromTimeapi.json()['currentUtcOffset']['seconds']
    responseFromTimeapi.close()
    with open('log.txt','a') as file:
        file.write(f'{utcToLocal('datetime')} Reset Cause: {resetCause} Battery voltage: {actual_voltage:.2f}\n')
    print(f'{utcToLocal('datetime')} Reset Cause: {resetCause} Battery voltage: {actual_voltage:.2f}')
batt_adc_power.value(0)
if actual_voltage < 4.40:
    buzzer = machine.PWM(machine.Pin(15),duty_u16=0)
    tone(buzzer,2500,1000)
    
'''
#Use esp32.wake_on_ext0 to allow a GPIO pin change wake it
'''
esp32.wake_on_ext0(interrupt_pin,esp32.WAKEUP_ANY_HIGH)
#machine.deepsleep(10000)
machine.deepsleep(900000000)
