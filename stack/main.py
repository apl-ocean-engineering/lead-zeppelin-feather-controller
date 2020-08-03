import time
import array
import math
import board

from nRF52840 import nRF52840 
from adalogger import RTC, SDCard 
from ultimate import GPS
from rfm9x import RFM9x 
from ms5837 import MS5837

sense = nRF52840()
clock = RTC()
card = SDCard()
gps = GPS()
radio = RFM9x()
pressure = MS5837()

logging = False
button_status = False

previous_time = time.monotonic()

tick = 1.0

def startup():
    radio.send_string("Hello, World!")

def next_tick():
    global previous_time 
    current_time = time.monotonic()
    if current_time - previous_time < tick:
        return False
    else:
        previous_time=current_time
        return True

def loop_update():
    global button_status
    global logging

    pressed = sense.pressed()
    if pressed and not button_status:
        print("Button Pressed")
        logging = not logging
    button_status = pressed

    gps.update()

def tick_update():
    if not logging:
        print("Pass")
        return

    print("Recording")

    sense.red(True) # turn on LED to indicate we're writing to the file
    print("Open")
    card.write("="*40+"\n")
    card.write("Relative Time: {:.3f}.\n".format(time.monotonic()))
    card.write("\n")

    t = clock.datetime()
    card.write("RTC Time: {}/{}/{} {:02}:{:02}:{:02}.\n".format(
                    t.tm_mday, t.tm_mon, t.tm_year,t.tm_hour, t.tm_min, t.tm_sec))
    card.write("\n")

    if gps.has_fix():
        print("Found fix.")
        timestamp_utc=gps.timestamp_utc()
        card.write(
            "GPS Time: {}/{}/{} {:02}:{:02}:{:02}.\n".format(
                timestamp_utc.tm_mday,  # Grab parts of the time from the
                timestamp_utc.tm_mon,  # struct_time object that holds
                timestamp_utc.tm_year,  # the fix time.  Note you might
                timestamp_utc.tm_hour,  # not get all data like year, day,
                timestamp_utc.tm_min,  # month!
                timestamp_utc.tm_sec,
            )
        )
        card.write("Latitude: {} degrees.\n".format(gps.latitude()))
        card.write("Longitude: {} degrees.\n".format(gps.longitude()))
        card.write("Fix quality: {}.\n".format(gps.fix_quality()))
        # Some attributes beyond latitude, longitude and timestamp are optional
        # and might not be present.  Check if they're None before trying to use!
        card.write("# satellites: {}.\n".format(gps.satellites()))
        card.write("Altitude: {} meters.\n".format(gps.altitude_m()))
        card.write("Speed: {} knots.\n".format(gps.speed_knots()))
        card.write("Track angle: {} degrees.\n".format(gps.track_angle_deg()))
        card.write("Horizontal dilution: {}.\n".format(gps.horizontal_dilution()))
        card.write("Height geo ID: {} meters.\n".format(gps.height_geoid()))
        card.write("\n")
    else:
        print("No GPS fix.")
        card.write("No GPS fix.")
        card.write("\n")

    radio.send("({},{},{})".format(gps.has_fix(), gps.latitude(), gps.longitude()))

    print("Proximity: {}.".format(sense.proximity()))
    card.write("Proximity: {}.\n".format(sense.proximity()))
    card.write("Red: {}, Green: {}, Blue: {}, Clear: {}.\n".format(*sense.color_data()))
    card.write("Temperature: {} C.\n".format(sense.temperature()))
    card.write("Barometric pressure: {}.\n".format(sense.pressure()))
    card.write("Altitude: {:.1f} m.\n".format(sense.altitude()))
    card.write("Magnetic: {} {} {} uTesla.\n".format(*sense.magnetic()))
    card.write("Acceleration: {} {} {} m/s^2.\n".format(*sense.acceleration()))
    card.write("Gyro: {} {} {} dps.\n".format(*sense.gyro()))
    card.write("Humidity: {}%.\n".format(sense.relative_humidity()))
    card.write("Sound level: {}.\n".format(sense.sound()))
    card.write("\n")

    pressure.read()
    card.write("Pressure: {} mbar.\n".format(pressure.pressure()))
    card.write("Temperature: {} deg C.\n".format(pressure.temperature()))
    card.write("Depth: {} m.\n".format(pressure.depth()))
    card.write("Altitude: {} m above mean sea level.\n".format(pressure.altitude()))

    sense.red(False)  # turn off LED to indicate we're done
    print("Close")

startup()
while True:
    loop_update()
    if next_tick():
        tick_update()
    

