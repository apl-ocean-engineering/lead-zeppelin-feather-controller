import time
import board
import busio

import adafruit_gps

class GPS:

    def __init__(self):
        self.uart = busio.UART(board.TX, board.RX, baudrate=9600, timeout=10)
        self.gps = adafruit_gps.GPS(self.uart, debug=False)
        self.gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0") # initialize
        self.gps.send_command(b"PMTK220,1000")

    def update(self):
        self.gps.update()

    def has_fix(self):
        return self.gps.has_fix

    def timestamp_utc(self):
        return self.gps.timestamp_utc

    def latitude(self):
        return self.gps.latitude

    def longitude(self):
        return self.gps.longitude

    def location(self):
        return (self.gps.latitude, self.gps.longitude)

    def fix_quality(self):
        return self.gps.fix_quality

    def altitude_m(self): # m
        return self.gps.altitude_m

    def speed_knots(self): # knots
        return self.gps.speed_knots

    def track_angle_deg(self):
        return self.gps.track_angle_deg

    def horizontal_dilution(self):
        return self.gps.horizontal_dilution

    def height_geoid(self):
        return self.gps.height_geoid
