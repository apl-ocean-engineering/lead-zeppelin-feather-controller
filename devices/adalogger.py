import io

import board
import busio
import digitalio
import microcontroller
import storage

import adafruit_pcf8523
import adafruit_sdcard

from .importwing import Wing

class RTC(Wing):
    def __init__(self):
        self.rtc = adafruit_pcf8523.PCF8523(Wing.i2c)

    def set_time(self, time): # (year, mon, date, hour, min, sec, wday, yday, isdst)
        self.rtc.datetime = time.struct_time(time)

    def datetime(self): # tm_mday, tm_mon, tm_year, tm_hour, tm_min, tm_sec
        return self.rtc.datetime

    def record(self):
        with io.StringIO() as output:
            t = self.datetime()
            output.write("RTC Time: {}/{}/{} {:02}:{:02}:{:02}.\n".format(
                            t.tm_mday, t.tm_mon, t.tm_year,t.tm_hour, t.tm_min, t.tm_sec))
            return output.getvalue()

class SDCard(Wing):
    def __init__(self, mount = "/sd", cs_pin = board.D10):
        self.mount = mount
        self.cs = digitalio.DigitalInOut(cs_pin)

        self.spi = Wing.spi
        self.sdcard = adafruit_sdcard.SDCard(self.spi, self.cs)
        self.vfs = storage.VfsFat(self.sdcard)
        storage.mount(self.vfs, self.mount)

    def write(self, string, filepath = Wing.filepath, mode = 'a'):
        with open(self.mount+filepath, mode) as f:
            f.write(string)

    