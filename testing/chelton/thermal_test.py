# Temperature
# Pressure
# Buzzer
# MCP3004
# Servo

import board
import time
import smbus

from CFS.Data.logger import setup_logging
from CFS.Sensors.temperature import Temperature
from CFS.Sensors.airpressure import Air_Pressure
from CFS.Sensors.voltage import Voltage
from CFS.Sensors.camera import Camera

from CFS.Data.backups import Backup

def get_height(pressure, temp):
    # This function is used to poll the pressure and temperature sensor to get altitude
    pressure = pressure * 100  # mbar to Pa
    temp = temp + 273.15  # c to Kelvin
    pressureSeaLevel = 101325  # in Pa

    # Derived from Hypsometric Formula
    return ((((pressureSeaLevel / pressure) ** (1 / 5.257)) - 1) * temp) / 0.0065

setup_logging("chelton_test")

i2c = board.I2C()  # uses board.SCL and board.SDA
bus = smbus.SMBus(1)


temperature_sensor = Temperature(i2c)
pressure_sensor = Air_Pressure(bus)
voltage = Voltage()

camera = Camera()

backup = Backup("Chelton", )

counter = 60 * 5
sleeptime = 5

camera.activate()

while counter > 0:
    temperature = temperature_sensor.get_data()
    pressure = pressure_sensor.get_data()
    pres_temp = pressure_sensor.get_temp()
    volt = voltage.get_data()
    height = get_height(pressure, temperature)

    print("- - - - -")
    print("Temperature: %.2fc" % temperature)
    print("Pressure: %.2f mbar" % pressure)
    print("Pressure Temprature: %.2fc" % pres_temp)
    print("Voltage: %.2fV" % volt)

    print("Est Height: ", height)

    backup.write("Temp: {}, Pressure: {}, Pres_Temp: {}, Voltage: {}, Height {}".format(temperature, pressure, pres_temp, volt, height))

    time.sleep(sleeptime)
    counter -= sleeptime

camera.deactivate()
