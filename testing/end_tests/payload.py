import logging
import time

from CFS.Data.logger import setup_logging
from CFS.payload import PayloadHardware

setup_logging("payload_sensor_test")
logger = logging.getLogger("Payload")
logger.info("Started Payload Logger")

payload = PayloadHardware(logger)

while True:
    #print("HC Temp: ", payload.pi.get_temp())
    #print("HC Load: ", payload.pi.get_load())
    #print("HC Disk: ", payload.pi.get_disk())

    #print("AP Pres: ", payload.air_pressure.get_data())
    #print("AP Temp: ", payload.air_pressure.get_temp())

    #print("Voltage: ", payload.voltage.get_data())

    print("IMU: ", payload.rotation.get_data())

    time.sleep(0.25)