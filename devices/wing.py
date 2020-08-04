import board
import busio

class Wing:
    uart = board.UART()
    spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
    try:
        i2c = board.I2C()
    except:
        print("No i2c!")
    filepath = "/log.txt"

    def refresh(self):
        pass

    def test(self):
        return True

    def record(self):
        return ""