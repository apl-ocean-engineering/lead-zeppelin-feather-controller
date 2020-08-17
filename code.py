import time
import math
import array
import sys
import board

import redirect

# looks at another file for the settings and tasks
# allows different setups to use different settings and tasks if necessary
reference = __import__(redirect.reference)

previous_time = time.monotonic()

def startup():
    print("Initalizing.")
    success = False
    device_success = {device_name:False for device_name in reference.devices}

    # loops through all devices until their tests are all successful
    
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

def next_tick(): # determines whether or not the next tick has arrived
    global previous_time
    current_time = time.monotonic()
    if current_time - previous_time < reference.tick:
        return False
    else:
        previous_time=current_time
        return True

def loop_update():
    # refreshes all devices
    for device in reference.devices.values():
        device.loop()

    check_mode()
    run_mode = reference.mode # separate variable in case the mode is changed midway
    
    # runs all tasks
    for task in reference.tasks[run_mode]:
        try:
            task.loop()
        except Exception as e:
            sys.print_exception(e)
            print("Failed executing loop function for task {} in mode {}.".format(task, run_mode))

    expire_tasks()

def tick_update():
    print("Tick at time {}.".format(time.monotonic()))
    print("Mode {}.".format(reference.mode))

    # refreshes all devices
    for device in reference.devices.values():
        device.tick()

    check_mode()
    run_mode = reference.mode # separate variable in case the mode is changed midway
        
    # runs all tasks
    for task in reference.tasks[reference.mode]:
        try:
            task.tick()
        except Exception as e:
            sys.print_exception(e)
            print("Failed executing tick function for command {} in mode {}.".format(task, run_mode))

    expire_tasks()

def check_mode(): # makes sure the current mode is actually valid
    if not reference.mode in reference.tasks:
        print("Invalid mode; resetting to default mode {}.".format(reference.default_mode))
        reference.mode = reference.default_mode

def expire_tasks(): # removes all expired tasks from the list 
    for mode_tasks in reference.tasks.values():
        for i in reversed(range(len(mode_tasks))): # reversed to prevent index problems
            if mode_tasks[i].expired():
                mode_tasks.pop(i).finish() # allows expired tasks to finish up

startup()
while True:
    loop_update()
    if next_tick():
        tick_update()


