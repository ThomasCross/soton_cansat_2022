import logging

from CFS.Data.logger import setup_logging
from CFS.container import ContainerHardware

setup_logging("container_sensor_test")
logger = logging.getLogger("Container")
logger.info("Started Container Logger")

container = ContainerHardware(logger)

while True:
    print("HC Temp: ", container.pi.get_temp())
    print("HC Load: ", container.pi.get_load())
    print("HC Disk: ", container.pi.get_disk())

    print("AP Pres: ", container.air_pressure.get_data())
    print("AP Temp: ", container.air_pressure.get_temp())

    print("GPS: ", container.gps.get_data())

    print("Temp: ", container.temperature.get_data())
    print("Voltage: ", container.voltage.get_data())

    input()