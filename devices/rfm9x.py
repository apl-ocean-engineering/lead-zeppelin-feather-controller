import random

import board
import busio
import digitalio

import adafruit_rfm9x

from .wing import Wing

# for the Adafruit LoRa Radio FeatherWing - RFM95W 433 MHz
# https://learn.adafruit.com/radio-featherwing/

# primarily one way communcations from the stack to the station
class RFM9x(Wing):
    def __init__(self, frequency=433.0, cs_pin=board.D9, reset_pin=board.D5):
        self.frequency = frequency
        self.cs = digitalio.DigitalInOut(board.D9)
        self.reset = digitalio.DigitalInOut(board.D5)

        self.spi = Wing.spi
        self.rfm9x = adafruit_rfm9x.RFM9x(self.spi, self.cs, self.reset, self.frequency)
        self.rfm9x.tx_power = 13

    def send(self, data):
        self.rfm9x.send(data)

    def send_string(self, string):
        self.send(bytes(string, "utf-8"))

    # if a handshake is received unexpectedly, completes the handshake
    def receive(self, timeout=0.5):
        data = self.rfm9x.receive(timeout=timeout)
        if data is not None and data[0]==0:
            return self.return_handshake(data)
        return data

    def receive_string(self, timeout=0.5):
        response = self.receive(timeout=timeout)
        if response is None:
            return None
        return str(response, "ascii")

    def last_rssi(self):
        return self.rfm9x.last_rssi

    # used by the station to receive a handshake when expected
    def return_handshake(self, packet):
        if packet is None or len(packet) !=2 or packet[0] != 0:
            return False
        a = packet[1]
        b = random.randint(0,254)
        self.send(bytes([a+1, b]))

        packet = self.receive(timeout=1)
        if packet is None or len(packet) !=2 or packet[0] != b+1:
            return False

        return True

    # used by the stack to send a handshake to ensure communications
    def send_handshake(self):
        a = random.randint(0,254)
        self.send(bytes([0,a]))
        
        packet = self.receive(timeout=1)
        if packet is None or len(packet) !=2 or packet[0] != a+1:
            return False

        b = packet[1]
        c = random.randint(0,254)
        self.send(bytes([b+1, c]))

        return True

    def test(self):
        return self.send_handshake()