import logging

from CFS.Data.logger import setup_logging
from CFS.payload import PayloadHardware

setup_logging("payload_mech_test")
logger = logging.getLogger("Payload")
logger.info("Started Payload Logger")

payload = PayloadHardware(logger)

print("A")


input()
payload.camera.activate()
payload.stabilisation.activate()

input()
payload.camera.deactivate()
payload.stabilisation.disable()

