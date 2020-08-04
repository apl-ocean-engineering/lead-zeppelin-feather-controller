import time
import array
import math
import board

from devices.nRF52840 import nRF52840 
from devices.adalogger import RTC, SDCard 
from devices.ultimate import GPS 
from devices.rfm9x import RFM9x 
from devices.bar30 import Bar30 

sense = nRF52840()
clock = RTC()
card = SDCard()
gps = GPS()
radio = RFM9x()
pressure = Bar30()

devices = []
devices.append(sense)
devices.append(clock)
devices.append(card)
devices.append(gps)
devices.append(radio)
devices.append(pressure)

logging = False
button_status = False

previous_time = time.monotonic()

tick = 1.0

def startup():
    for device in devices:
        assert device.test()
    print("Initialization successful.")

def next_tick():
    global previous_time 
    current_time = time.monotonic()
    if current_time - previous_time < tick:
        return False
    else:
        previous_time=current_time
        return True

def loop_update():
    global button_status
    global logging

    pressed = sense.pressed()
    if pressed and not button_status:
        print("Button Pressed")
        logging = not logging
    button_status = pressed

    gps.update()

def tick_update():
    if not logging:
        print("Pass")
        return

    print("Fix: {}".format(gps.has_fix()))
    radio.send_string("{}, {}, {}".format(gps.has_fix(),gps.latitude(),gps.longitude()))

    print("Recording")
    sense.red(True) # turn on LED to indicate we're writing to the file
    for device in devices:
        device.refresh()
        info = device.record()
        print(info)
        card.write(info)
    sense.red(False)  # turn off LED to indicate we're done
    print("Close")

startup()
while True:
    loop_update()
    if next_tick():
        tick_update()
    

