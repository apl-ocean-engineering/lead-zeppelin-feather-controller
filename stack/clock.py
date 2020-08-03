import busio
import time
import board

import adafruit_pcf8523

class Clock:
    def __init__(self):
        self.rtc = adafruit_pcf8523.PCF8523(board.I2C())

    def set_time(self, time): # (year, mon, date, hour, min, sec, wday, yday, isdst)
        self.rtc.datetime = time.struct_time(time)

    def get_time(self): # tm_mday, tm_mon, tm_year, tm_hour, tm_min, tm_sec
        return self.rtc.datetime