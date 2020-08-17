import board
import busio

# generic class for the boards

class Wing:
    # variables defined here to prevent multiple instances from being created
    uart = busio.UART(board.TX, board.RX, baudrate=9600, timeout=10)
    spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
    try:
        i2c = board.I2C()
    except:
        print("No i2c!")
    filepath = "/log.txt"

    # runs once per program loop (loops run as fast as possible)
    def loop(self):
        pass

    # runs once per tick (tick rate defined in settings)
    def tick(self):
        pass

    # tests if the device is working and active
    def test(self):
        return True

    # returns a string with current sensor data
    def string(self):
        return ""