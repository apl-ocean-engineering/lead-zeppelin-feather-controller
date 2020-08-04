import time
import io

import board
import busio

import adafruit_gps

from wing import Wing

class GPS(Wing):

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

    def satellites(self):
        return self.gps.satellites

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

    def refresh(self):
        self.update()

    def record(self):
        with io.StringIO() as output:
            timestamp_utc = self.timestamp_utc()
            output.write(
                "GPS Time: {}/{}/{} {:02}:{:02}:{:02}.\n".format(
                    timestamp_utc.tm_mday,  # Grab parts of the time from the
                    timestamp_utc.tm_mon,  # struct_time object that holds
                    timestamp_utc.tm_year,  # the fix time.  Note you might
                    timestamp_utc.tm_hour,  # not get all data like year, day,
                    timestamp_utc.tm_min,  # month!
                    timestamp_utc.tm_sec,
                )
            )

            output.write("Fix: {}.\n".format(self.has_fix()))

            output.write("Latitude: {} degrees.\n".format(self.latitude()))
            output.write("Longitude: {} degrees.\n".format(self.longitude()))
            output.write("Fix quality: {}.\n".format(self.fix_quality()))

            output.write("# satellites: {}.\n".format(self.satellites()))
            output.write("Altitude: {} meters.\n".format(self.altitude_m()))
            output.write("Speed: {} knots.\n".format(self.speed_knots()))
            output.write("Track angle: {} degrees.\n".format(self.track_angle_deg()))
            output.write("Horizontal dilution: {}.\n".format(self.horizontal_dilution()))
            output.write("Height geo ID: {} meters.\n".format(self.height_geoid()))

            return output.getvalue()