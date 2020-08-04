import board
import busio

class Wing:
    i2c = board.I2C()
    spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
    filepath = "/log.txt"

    def refresh(self):

    def test(self):
        return True
        pass

    def record(self):
        return ""