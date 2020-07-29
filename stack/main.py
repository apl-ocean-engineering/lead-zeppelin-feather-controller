import time
import array
import math
import board
import neopixel
import audiobusio
import digitalio
import busio
import digitalio
import microcontroller
import storage

import adafruit_apds9960.apds9960
import adafruit_bmp280
import adafruit_lis3mdl
import adafruit_lsm6ds
import adafruit_sht31d
import adafruit_pcf8523
import adafruit_sdcard
import adafruit_gps
import adafruit_rfm9x

# board basics
i2c = board.I2C()
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)

# board sensors
apds9960 = adafruit_apds9960.apds9960.APDS9960(i2c)
bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c)
lis3mdl = adafruit_lis3mdl.LIS3MDL(i2c)
lsm6ds33 = adafruit_lsm6ds.LSM6DS33(i2c)
sht31d = adafruit_sht31d.SHT31D(i2c)
microphone = audiobusio.PDMIn(board.MICROPHONE_CLOCK, board.MICROPHONE_DATA,
                            sample_rate=16000, bit_depth=16)

apds9960.enable_proximity = True
apds9960.enable_color = True

# local pressure
bmp280.sea_level_pressure = 1013.885

def normalized_rms(values):
    minbuf = int(sum(values) / len(values))
    return int(math.sqrt(sum(float(sample - minbuf) *
                             (sample - minbuf) for sample in values) / len(values)))
def sound():
    samples = array.array('H', [0] * 160)
    microphone.record(samples, len(samples))
    return normalized_rms(samples)

# storage settings
sd_cs = digitalio.DigitalInOut(board.D10)
mount = "/sd"

# connect to the card and mount the filesystem.
sdcard = adafruit_sdcard.SDCard(spi, sd_cs)
vfs = storage.VfsFat(sdcard)
storage.mount(vfs, mount)

# real time clock
rtc = adafruit_pcf8523.PCF8523(i2c)
days = ("Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday")

# gps
uart = busio.UART(board.TX, board.RX, baudrate=9600, timeout=10)
gps = adafruit_gps.GPS(uart, debug=False)  # Use UART/pyserial
gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0") # basic info
gps.send_command(b"PMTK220,1000") # update rate

# radio settings
radio_frequency = 433.0  
radio_cs = digitalio.DigitalInOut(board.D9)
radio_reset = digitalio.DigitalInOut(board.D5)

# radio config
rfm9x = adafruit_rfm9x.RFM9x(spi, radio_cs, radio_reset, radio_frequency)
rfm9x.tx_power = 23

def send(string):
    rfm9x.send(bytes(string, "utf-8"))

# status LED
red_led = digitalio.DigitalInOut(board.D13)
red_led.direction = digitalio.Direction.OUTPUT

# start/stop button
button = digitalio.DigitalInOut(board.SWITCH)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP # pressed = False. pull must be UP, or button.value will always be false

def button_pressed():
    return not button.value

logging = False
button_status = False

previous_time=time.monotonic()

tick = 1.0

def startup():
    send("Hello, World!")

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

    pressed = button_pressed()
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
    with open("/sd/log.txt", "a") as f:
        red_led.value = True  # turn on LED to indicate we're writing to the file
        print("Open")
        f.write("="*40+"\n")
        f.write("Relative Time: {:.3f}.\n".format(time.monotonic()))
        f.write("\n")

        t = rtc.datetime
        f.write("RTC Time: {}/{}/{} {:02}:{:02}:{:02}.\n".format(
                        t.tm_mday, t.tm_mon, t.tm_year,t.tm_hour, t.tm_min, t.tm_sec))
        f.write("\n")

        if gps.has_fix:
            print("Found fix.")
            f.write(
                "GPS Time: {}/{}/{} {:02}:{:02}:{:02}.\n".format(
                    gps.timestamp_utc.tm_mday,  # Grab parts of the time from the
                    gps.timestamp_utc.tm_mon,  # struct_time object that holds
                    gps.timestamp_utc.tm_year,  # the fix time.  Note you might
                    gps.timestamp_utc.tm_hour,  # not get all data like year, day,
                    gps.timestamp_utc.tm_min,  # month!
                    gps.timestamp_utc.tm_sec,
                )
            )
            f.write("Latitude: {0:.6f} degrees.\n".format(gps.latitude))
            f.write("Longitude: {0:.6f} degrees.\n".format(gps.longitude))
            f.write("Fix quality: {}.\n".format(gps.fix_quality))
            # Some attributes beyond latitude, longitude and timestamp are optional
            # and might not be present.  Check if they're None before trying to use!
            f.write("# satellites: {}.\n".format(gps.satellites))
            f.write("Altitude: {} meters.\n".format(gps.altitude_m))
            f.write("Speed: {} knots.\n".format(gps.speed_knots))
            f.write("Track angle: {} degrees.\n".format(gps.track_angle_deg))
            f.write("Horizontal dilution: {}.\n".format(gps.horizontal_dilution))
            f.write("Height geo ID: {} meters.\n".format(gps.height_geoid))
            f.write("\n")
        else:
            print("No GPS fix.")
            f.write("No GPS fix.")
            f.write("\n")

        send("({},{:.6f},{:.6f})".format(gps.has_fix, gps.latitude, gps.longitude))

        samples = array.array('H', [0] * 160)
        microphone.record(samples, len(samples))

        print("Proximity: {}.".format(apds9960.proximity))
        f.write("Proximity: {}.\n".format(apds9960.proximity))
        f.write("Red: {}, Green: {}, Blue: {}, Clear: {}.\n".format(*apds9960.color_data))
        f.write("Temperature: {:.1f} C.\n".format(bmp280.temperature))
        f.write("Barometric pressure: {}.\n".format(bmp280.pressure))
        f.write("Altitude: {:.1f} m.\n".format(bmp280.altitude))
        f.write("Magnetic: {:.3f} {:.3f} {:.3f} uTesla.\n".format(*lis3mdl.magnetic))
        f.write("Acceleration: {:.2f} {:.2f} {:.2f} m/s^2.\n".format(*lsm6ds33.acceleration))
        f.write("Gyro: {:.2f} {:.2f} {:.2f} dps.\n".format(*lsm6ds33.gyro))
        f.write("Humidity: {:.1f}%.\n".format(sht31d.relative_humidity))
        f.write("Sound level: {}.\n".format(normalized_rms(samples)))
        f.write("\n")

        red_led.value = False  # turn off LED to indicate we're done
        print("Close")

startup()
while True:
    loop_update()
    if next_tick():
        tick_update()
    

