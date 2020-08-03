import board
import busio

class Wing:
    i2c = board.I2C()
    spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
