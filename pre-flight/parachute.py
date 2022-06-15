import logging

from CFS.Data.logger import setup_logging
from CFS.container import ContainerHardware

setup_logging("container_mech_test")
logger = logging.getLogger("Container")
logger.info("Started Container Logger")

container = ContainerHardware(logger)

input()
container.parachute.activate()