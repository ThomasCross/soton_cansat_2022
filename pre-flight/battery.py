from CFS.Data.logger import setup_logging
from CFS.Sensors.voltage import Voltage

setup_logging("battery-pre-flight")

voltage = Voltage()

print("Voltage: %.2fV" % voltage.get_data())

