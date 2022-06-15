# Temperature
# Pressure
# Buzzer
# MCP3004
# Servo

import board
from digitalio import DigitalInOut
import time

from CFS.Data.logger import setup_logging
from CFS.Sensors.rotation import Rotation

setup_logging("imu_test")

scl = board.SCL
sda = board.SDA
reset_pin = DigitalInOut(board.D5)

imu = Rotation(scl, sda, reset_pin)

while True:
    imu_data = imu.get_data()

    print(imu_data)
    input()

