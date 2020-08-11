import board
import busio

class Wing:
    uart = busio.UART(board.TX, board.RX, baudrate=9600, timeout=10)
    spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
    try:
        i2c = board.I2C()
    except:
        print("No i2c!")
    filepath = "/log.txt"

    def loop(self):
        pass

    def tick(self):
        pass

    def test(self):
        return True

    def string(self):
        return ""