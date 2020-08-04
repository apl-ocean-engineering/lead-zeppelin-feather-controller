import board
import busio

class Wing:
    i2c = board.I2C()
    spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
    filepath = "/log.txt"

    def refresh(self):
        pass

    def record(self):
        return ""