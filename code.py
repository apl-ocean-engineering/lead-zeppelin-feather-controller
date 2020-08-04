import time
import array
import math
import board
import microcontroller

from devices.rfm9x import RFM9x 

radio = RFM9x()

previous_time = time.monotonic()

tick = 1.0

def startup():
    while not radio.send_handshake():
        print("Attempting handshake.")
    radio.send_string("Station.")
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
    print(microcontroller.cpu.temperature)
    radio.send_string(str(microcontroller.cpu.temperature))

startup()
while True:
    loop_update()
    if next_tick():
        tick_update()
    

