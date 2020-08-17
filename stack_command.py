import sys

from task import Task

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

devices = { # used by code.py to regularly refresh all devices
    "sense"     : sense,
    "ble"       : ble,
    "clock"     : clock,
    "card"      : card,
    "gps"       : gps,
    "radio"     : radio,
    "pressure"  : pressure,
}

mode_idle = "i"
mode_active = "a"

mode = mode_idle # current mode; also is the initial mode on startup
default_mode = mode_idle # default mode if an invalid mode is detected
tick = 1.0 # duration of each tick, in seconds

this = __import__("stack_command")

# button
class Bu(Task):
    def __init__(self, *args):
        super().__init__()
        self.pressed = False

    def loop(self): 
        global mode
        current = sense.pressed()
        if current and not self.pressed:
            if mode == mode_idle:
                mode = mode_active
            else:
                mode = default_mode
        self.pressed = current

    def core(self): 
        return True


# radio gps
class RG(Task):
    def __init__(self, *args): 
        super().__init__()

    def tick(self): 
        radio.send_string("{}, {}, {}".format(gps.has_fix(),gps.latitude(),gps.longitude()))

    def core(self): 
        return True

# bluetooth
class BT(Task):
    def __init__(self, *args): 
        super().__init__()
        self.hold = ""
        self.valid = True

    def tick(self):     
        self.read()

    def read(self):
        while ble.in_waiting():
            command_complete = False
            while ble.in_waiting() and not command_complete:
                char = chr(ble.read(1)[0])
                try:
                    self.hold += char
                except Exception as e:
                    sys.print_exception(e)
                    self.report("Invalid char.")
                    self.valid = False
                if char == '\n':
                        command_complete = True

            if command_complete:
                if self.valid:
                    try:
                        self.execute_command(self.hold)
                    except Exception as e:
                        sys.print_exception(e)
                        self.report("Exception.")
                else:
                    self.valid = True
                    self.report("Invalid, skipping.")
                self.hold = ""

    def execute_command(self, command):
        self.report("Executing {}".format(command))
        parts = command.split()
        if parts[0]=="a":
            self.add(parts)
        elif parts[0]=="d":
            self.delete(parts)
        elif parts[0]=="l":
            self.list_tasks(parts)
        elif parts[0]=="m":
            self.change_mode(parts)
        else:
            self.report("No command.")

    def add(self, parts):
        mode = parts[1]
        task_name = parts[2]
        args = parts[3:]
        task_class = getattr(this, task_name)
        task = task_class(*args)
        tasks[mode].append(task)

    def delete(self, parts):
        mode = parts[1]
        index = int(parts[2])
        tasks[mode][index].expire()

    def list_tasks(self, parts):
        for mode in tasks:
            self.report("Mode {}:\n".format(mode))
            task_list = tasks[mode]
            for i in range(len(task_list)):
                self.report("Task: {}; Instance: {}; Core?: {}\n".format(i, task_list[i], task_list[i].core()))

    def change_mode(self, parts):
        if len(parts)<2:
            self.report(this.mode)
        else:
            change = parts[1]
            this.mode = change

    def clear(self):
        self.hold=""

    def report(self, string):
        print(string, end="")
        ble.write(string)

    def core(self): 
        return True

# data log
class DL(Task): 
    def __init__(self, *args): 
        super().__init__()
        self.counter = 0
        self.slow = 10

    def tick(self): 
        if mode == default_mode:
            self.counter+=1
            if self.counter % self.slow:
                return

        print("Writing.")
        sense.red(True)

        card.write("="*40)
        for device in devices.values():
            info = device.string()
            # print(info)
            card.write(info)
            card.write("\n")

        sense.red(False)
        print("Done writing.")

    def core(self): 
        return True

# blue blink
class BB(Task):
    def __init__(self, *args):
        super().__init__()
        self.light = False
        self.counter=10
        if len(args)>0:
            self.counter = int(args[0])

    def tick(self):
        sense.blue(self.light)
        self.light = not self.light
        self.counter -=1
        if self.counter <0:
            self.stop=True

    def finish(self):
        sense.blue(False)

button = Bu()
radio_gps = RG()
bluetooth = BT()
datalog = DL()
blink = BB()

task_idle = [
    button, 
    blink, 
    bluetooth, 
    datalog,
    ]

task_active = [
    button, 
    radio_gps, 
    bluetooth, 
    datalog,
    ]

tasks = { # used by code.py to run the relevant tasks
    mode_idle      : task_idle,
    mode_active    : task_active,
}