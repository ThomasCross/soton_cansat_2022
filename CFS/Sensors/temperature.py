from CFS.Sensors.sensor import Sensor, SensorIDs
import adafruit_tmp117


class Temperature(Sensor):
    # ID: 2
    # Type: Temperature
    # Model: TMP117

    # Comm Method: I2C
    # I2C Device Address (Handled by library)

    device = None

    def __init__(self, i2c):
        # Initialises Temperature sensor class, passes type and ID to super class.
        # i2c is board 'i2c = board.I2C()'
        super().__init__("Temperature", SensorIDs.TEMPERATURE)

        self.device = adafruit_tmp117.TMP117(i2c)

    def get_data(self):
        # Used to get data from the temperature sensor
        return self.device.temperature