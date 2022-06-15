import logging

from CFS.Data.logger import setup_logging
from CFS.container import ContainerHardware

setup_logging("container_mech_test")
logger = logging.getLogger("Container")
logger.info("Started Container Logger")

container = ContainerHardware(logger)

print("Move Chute")
input()
container.parachute.activate()

print("Move Payload")
input()
container.payload.activate()

print("Buzz")
input()
container.buzzer.activate()