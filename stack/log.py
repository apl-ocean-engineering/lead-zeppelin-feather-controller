import board
import busio
import digitalio
import microcontroller
import storage

import adafruit_sdcard

class Log:
    def __init__(self, mount = "sd", pin = board.D10):
        self.mount = mount
        cs = digitalio.DigitalInOut(pin)

        spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
        sdcard = adafruit_sdcard.SDCard(spi, cs)
        vfs = storage.VfsFat(sdcard)
        storage.mount(vfs, mount)

    def write(self, string, filename = 'log.txt', mode = 'a'):
        with open(self.mount + filename, mode) as f:
            f.write(string)

    