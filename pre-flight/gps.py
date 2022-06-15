import time

import smbus

from CFS.Data.logger import setup_logging
from CFS.Sensors.gps import GPS

setup_logging("gps_calibration")

bus = smbus.SMBus(1)

gps = GPS(bus)
gps.activate()

while True:
    gps_data = gps.get_data()

    print("Timestamp: ", gps_data[0])
    print("Lat: ", gps_data[1])
    print("Long: ", gps_data[2])
    print("Alt: ", gps_data[3])
    print("Sat: ", gps_data[4])
    print(" - - - - - - - - - - - - - - - - ")

    time.sleep(1)

