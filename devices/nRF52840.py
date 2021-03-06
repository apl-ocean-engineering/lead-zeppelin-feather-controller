import io
import time
import array
import math

import board
import audiobusio
import digitalio
import neopixel

import adafruit_apds9960.apds9960
import adafruit_bmp280
import adafruit_lis3mdl
import adafruit_lsm6ds
import adafruit_sht31d

from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService

from .wing import Wing

# for the Adafruit Feather nRF52840 Sense
# https://learn.adafruit.com/adafruit-feather-sense

class Sense(Wing):
    def __init__(self):
        self.i2c = Wing.i2c

        self.apds9960 = adafruit_apds9960.apds9960.APDS9960(self.i2c)
        self.bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(self.i2c)
        self.lis3mdl = adafruit_lis3mdl.LIS3MDL(self.i2c)
        self.lsm6ds33 = adafruit_lsm6ds.LSM6DS33(self.i2c)
        self.sht31d = adafruit_sht31d.SHT31D(self.i2c)
        self.microphone = audiobusio.PDMIn(board.MICROPHONE_CLOCK, board.MICROPHONE_DATA,
                                    sample_rate=16000, bit_depth=16)

        self.apds9960.enable_proximity = True
        self.apds9960.enable_color = True

        # set to local sea level pressure
        self.bmp280.sea_level_pressure = 1013.25

        # input button
        self.button = digitalio.DigitalInOut(board.SWITCH)
        self.button.direction = digitalio.Direction.INPUT
        self.button.pull = digitalio.Pull.UP # pressed = False. pull must be UP, or button.value will always be false

        # status LEDs
        self.red_led = digitalio.DigitalInOut(board.RED_LED)
        self.red_led.direction = digitalio.Direction.OUTPUT
        self.blue_led = digitalio.DigitalInOut(board.BLUE_LED)
        self.blue_led.direction = digitalio.Direction.OUTPUT

    def pressed(self):
        return not self.button.value

    def red(self,value):
        self.red_led.value=value

    def blue(self,value):
        self.blue_led.value=value

    def proximity(self):
        return self.apds9960.proximity

    def color_data(self): # RGBA
        return self.apds9960.color_data

    def temperature(self): # C
        return self.bmp280.temperature

    def pressure(self): 
        return self.bmp280.pressure

    def altitude(self): # m
        return self.bmp280.altitude

    def magnetic(self): # uTesla
        return self.lis3mdl.magnetic

    def acceleration(self): # m/s^2
        return self.lsm6ds33.acceleration

    def gyro(self): # dps
        return self.lsm6ds33.gyro
        
    def relative_humidity(self):
        return self.sht31d.relative_humidity

    def sound(self):
        samples = array.array('H', [0] * 160)
        self.microphone.record(samples, len(samples))
        return normalized_rms(samples)

    def string(self):
        with io.StringIO() as output:
            output.write("Proximity: {}.\n".format(self.proximity()))
            output.write("Red: {}, Green: {}, Blue: {}, Clear: {}.\n".format(*self.color_data()))
            output.write("Temperature: {} C.\n".format(self.temperature()))
            output.write("Barometric pressure: {}.\n".format(self.pressure()))
            output.write("Altitude: {:.1f} m.\n".format(self.altitude()))
            output.write("Magnetic: {} {} {} uTesla.\n".format(*self.magnetic()))
            output.write("Acceleration: {} {} {} m/s^2.\n".format(*self.acceleration()))
            output.write("Gyro: {} {} {} dps.\n".format(*self.gyro()))
            output.write("Humidity: {}%.\n".format(self.relative_humidity()))
            output.write("Sound level: {}.\n".format(self.sound()))

            return output.getvalue()

def normalized_rms(values):
    minbuf = int(sum(values) / len(values))
    return int(math.sqrt(sum(float(sample - minbuf) *
                            (sample - minbuf) for sample in values) / len(values)))

# used for two way close range communication 
class BLE(Wing):
    def __init__(self):
        self.ble = BLERadio()
        self.uart = UARTService()
        self.advertisement = ProvideServicesAdvertisement(self.uart)
        self.ble.start_advertising(self.advertisement)

    def connected(self):
        return self.ble.connected

    def in_waiting(self):
        return self.uart.in_waiting

    # presumably is best effort?
    def read(self, nbytes=None):
        return self.uart.read(nbytes)

    def read_string(self, nbytes=None):
        response = self.read(nbytes=nbytes)
        if response is None:
            return None
        return str(response, "ascii")

    def write(self, data):
        self.uart.write(data)

    def write_string(self, string):
        self.write(bytes(string))

    def test(self):
        return self.connected()