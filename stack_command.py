from command import Command

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

devices = {
    "sense"     : sense,
    "ble"       : ble,
    "clock"     : clock,
    "card"      : card,
    "gps"       : gps,
    "radio"     : radio,
    "pressure"  : pressure,
}

mode = "idle"
default_mode = "idle"
tick = 1.0

class ButtonModeChange(Command):
    def __init__(self, *args):
        self.pressed = False

    def loop(self): 
        global mode
        current = sense.pressed()
        if current and not self.pressed:
            if mode == default_mode:
                mode = "active"
            else:
                mode = default_mode
        self.pressed = current

    def core(self): 
        return True

class RadioGPSUpdate(Command):
    def __init__(self, *args): 
        pass

    def tick(self): 
        radio.send_string("{}, {}, {}".format(gps.has_fix(),gps.latitude(),gps.longitude()))

    def core(self): 
        return True

class BluetoothRespond(Command):
    def __init__(self, *args): 
        pass

    def tick(self):     
        num = ble.in_waiting()
        print("Bluetooth {} bytes available.".format(num))
        read = ble.read(num)
        print(str(read, "ascii"))
        ble.write(read)

    def core(self): 
        return True

class DataLog(Command):
    def __init__(self, *args): 
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

bmc = ButtonModeChange()
radio_gps = RadioGPSUpdate()
bluetooth = BluetoothRespond()
datalog = DataLog()

idle_commands = [bmc, datalog]
active_commands = [bmc, radio_gps, bluetooth, datalog]

commands = {
    "idle"      : idle_commands,
    "active"    : active_commands,
}