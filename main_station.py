import time
import array
import math
import board

from devices.rfm9x import RFM9x 

radio = RFM9x()

logging = False
button_status = False

previous_time = time.monotonic()

tick = 1.0

def startup():
    while not radio.receive():
        print("Waiting.")
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
    pass

def tick_update():
    string = radio.receive()
    print(string)

startup()
while True:
    loop_update()
    if next_tick():
        tick_update()
    

