import io

from .wing import Wing
from .ms5837 import MS5837_30BA

# for the Bar30 High-Resolution 300m Depth/Pressure Sensor
# https://bluerobotics.com/store/sensors-sonars-cameras/sensors/bar30-sensor-r1/

class Bar30(Wing):
    def __init__(self):
        self.sensor = MS5837_30BA()
        assert self.sensor.init()

    # sensors need to be updated each time prior to receiving data
    def read(self):
        self.sensor.read()

    def setFluidDensity(self, density):
        self.sensor.setFluidDensity(density)

    def pressure(self):
        return self.sensor.pressure()

    def temperature(self):
        return self.sensor.temperature()
    
    def depth(self):
        return self.sensor.depth()

    def altitude(self):
        return self.sensor.altitude()

    def refresh(self):
        self.read()

    def string(self):
        with io.StringIO() as output:
            output.write("Pressure: {} mbar.\n".format(self.pressure()))
            output.write("Temperature: {} deg C.\n".format(self.temperature()))
            output.write("Depth: {} m.\n".format(self.depth()))
            output.write("Altitude: {} m above mean sea level.\n".format(self.altitude()))
            return output.getvalue()