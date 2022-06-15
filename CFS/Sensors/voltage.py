from CFS.Sensors.sensor import Sensor, SensorIDs
import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3004 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn


class Voltage(Sensor):
    # ID: 4
    # Type: Battery Voltage
    # Model: MCP3004

    # Comm Method: SPI

    def __init__(self):
        # Initialises Voltage sensor class, passes type and ID to super class.
        super().__init__("Voltage", SensorIDs.VOLTAGE)

        # create the spi bus
        spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)

        # create the cs (chip select)
        cs = digitalio.DigitalInOut(board.D5)

        # create the mcp object
        mcp = MCP.MCP3004(spi, cs, ref_voltage=3.3 * 2.6185)

        # create an analog input channel on pin 0
        self.chan = AnalogIn(mcp, MCP.P0)

    def get_data(self):
        # Used to get data from the temperature sensor
        return self.chan.voltage