import time
import math
import array
import sys
import board

import redirect

reference = __import__(redirect.reference)

previous_time = time.monotonic()

def startup():
    print("Initalizing.")
    success = False
    device_success = {device_name:False for device_name in reference.devices}
    while not success:
        print("Loop.")
        success = True
        for device_name, device in reference.devices.items():
            if device_success[device_name]:
                continue
            
            try:
                assert device.test()
                device_success[device_name]=True
                print("Test success for device {} named {}.".format(device,device_name))
            except Exception as e:
                # sys.print_exception(e)
                print("Test failed for device {} named {}.".format(device,device_name))
                success = False
        time.sleep(reference.tick)
    print("Initialization successful.")

def next_tick(): 
    global previous_time
    current_time = time.monotonic()
    if current_time - previous_time < reference.tick:
        return False
    else:
        previous_time=current_time
        return True

def loop_update():
    for device in reference.devices.values():
        device.loop()

    check_mode()
    run_mode = reference.mode
        
    for command in reference.commands[reference.mode]:
        try:
            command.loop()
        except Exception as e:
            sys.print_exception(e)
            print("Failed executing loop function for command {} in mode {}.".format(command, run_mode))

    clear_commands()

def tick_update():
    print("Tick at time {}.".format(time.monotonic()))
    print("Mode {}.".format(reference.mode))
    for device in reference.devices.values():
        device.tick()

    check_mode()
    run_mode = reference.mode
        
    for command in reference.commands[reference.mode]:
        try:
            command.tick()
        except Exception as e:
            sys.print_exception(e)
            print("Failed executing tick function for command {} in mode {}.".format(command, run_mode))

    clear_commands()

def check_mode():
    if not reference.mode in reference.commands:
        print("Invalid mode; resetting to default mode {}.".format(reference.default_mode))
        reference.mode=reference.default_mode

def clear_commands():
    for mode_commands in reference.commands.values():
        mode_commands = [x for x in mode_commands if x.core() or not x.expired()]

startup()
while True:
    loop_update()
    if next_tick():
        tick_update()


