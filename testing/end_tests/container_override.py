import logging
import time

from CFS.Data.logger import setup_logging
from CFS.container import ContainerHardware

setup_logging("container_sensor_test")
logger = logging.getLogger("Container")
logger.info("Started Container Logger")

container = ContainerHardware(logger)

print("AP Pres 1: ", container.air_pressure.get_data())
time.sleep(0.5)
print("AP Pres 1: ", container.air_pressure.get_data())
time.sleep(0.5)
print("AP Pres 1: ", container.air_pressure.get_data())
time.sleep(0.5)
print("AP Pres 1: ", container.air_pressure.get_data())
time.sleep(0.5)
print("AP Pres 1: ", container.air_pressure.get_data())
time.sleep(0.5)

print()

container.air_pressure.start_override()
container.air_pressure.input_sim_data(50)
print("AP Pres 2: ", container.air_pressure.get_data())
time.sleep(0.5)

container.air_pressure.input_sim_data(51)
print("AP Pres 2: ", container.air_pressure.get_data())
time.sleep(0.5)

container.air_pressure.input_sim_data(52)
print("AP Pres 2: ", container.air_pressure.get_data())
time.sleep(0.5)

container.air_pressure.input_sim_data(53)
print("AP Pres 2: ", container.air_pressure.get_data())
time.sleep(0.5)

container.air_pressure.input_sim_data(54)
print("AP Pres 2: ", container.air_pressure.get_data())
time.sleep(0.5)

print()

container.air_pressure.stop_override()
print("AP Pres 3: ", container.air_pressure.get_data())
time.sleep(0.5)
print("AP Pres 3: ", container.air_pressure.get_data())
time.sleep(0.5)
print("AP Pres 3: ", container.air_pressure.get_data())
time.sleep(0.5)
print("AP Pres 3: ", container.air_pressure.get_data())
time.sleep(0.5)
print("AP Pres 3: ", container.air_pressure.get_data())
time.sleep(0.5)