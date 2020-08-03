import board
import busio
import digitalio
import microcontroller
import storage

import adafruit_pcf8523
import adafruit_sdcard

import os

from wing import Wing

class RTC(Wing):
    def __init__(self):
        self.rtc = adafruit_pcf8523.PCF8523(Wing.i2c)

    def set_time(self, time): # (year, mon, date, hour, min, sec, wday, yday, isdst)
        self.rtc.datetime = time.struct_time(time)

    def datetime(self): # tm_mday, tm_mon, tm_year, tm_hour, tm_min, tm_sec
        return self.rtc.datetime

class SDCard(Wing):
    def __init__(self, mount = "/sd", cs_pin = board.D10):
        self.mount = mount
        self.cs = digitalio.DigitalInOut(cs_pin)

        self.spi = Wing.spi
        self.sdcard = adafruit_sdcard.SDCard(self.spi, self.cs)
        self.vfs = storage.VfsFat(self.sdcard)
        storage.mount(self.vfs, self.mount)

    def write(self, string, filename = 'log.txt', mode = 'a'):
        with open(self.mount+"/"+filename, mode) as f:
            f.write(string)

    