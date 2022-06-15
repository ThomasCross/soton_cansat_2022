import logging

from CFS.Data.logger import setup_logging


setup_logging("testing")
logger = logging.getLogger("Test Logger")

logger.info("Created Logger")
logger.info("Info")
logger.debug("Debug")
logger.error("Error")
logger.warning("Warning")
logger.critical("Ahh Fuck")
logger.info("Finished")
