import time
import math
import array
import sys
import board

from devices.nRF52840 import Sense, BLE 
from devices.adalogger import RTC, SDCard 
from devices.ultimate import GPS 
from devices.rfm9x import RFM9x 
from devices.bar30 import Bar30 

sense = Sense()
ble = BLE()
clock = RTC()
card = SDCard()
gps = GPS()
radio = RFM9x()
pressure = Bar30()

devices = []
devices.append(sense)
devices.append(ble)
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
    print("Initalizing.")
    success = False
    device_success = [False for device in devices]
    while not success:
        success = True
        for i in range(len(devices)):
            if device_success[i]:
                continue
            
            device = devices[i]
            try:
                assert device.test()
                device_success[i]=True
            except Exception:
                print("Test failed for device {} (index {}).".format(device, i))
                success = False
        time.sleep(tick)
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

    num = ble.in_waiting()
    print("Bluetooth {} bytes available.".format(num))
    read = ble.read(num)
    print(read)
    print(str(read, "ascii"))
    ble.write(read)

    print("Recording")
    sense.red(True) # turn on LED to indicate we're writing to the file
    for device in devices:
        device.refresh()
        info = device.string()
        # print(info)
        card.write(info)
    sense.red(False)  # turn off LED to indicate we're done
    print("Close")

startup()
while True:
    loop_update()
    if next_tick():
        tick_update()
    

