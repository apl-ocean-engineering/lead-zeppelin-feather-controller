import board
import busio
import digitalio

import adafruit_rfm9x

class Radio:
    def __init__(self, frequency=433.0, cs_pin=board.D9, reset_pin=board.D5):
        self.frequency = frequency
        self.cs = digitalio.DigitalInOut(board.D9)
        self.reset = digitalio.DigitalInOut(board.D5)

        self.spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
        self.rfm9x = adafruit_rfm9x.RFM9x(self.spi, self.cs, self.reset, self.frequency)
        self.rfm9x.tx_power = 23

    def send(self, data):
        self.rfm9x.send(data)

    def send_string(self, string):
        self.send(bytes(string, "utf-8"))

    def receive(self, duration=0.5):
        return self.rfm9x.receive(duration)

    def receive_string(self, duration):
        return str(self.receive(duration), "ascii")

    def last_rssi(self):
        return self.rfm9x.last_rssi