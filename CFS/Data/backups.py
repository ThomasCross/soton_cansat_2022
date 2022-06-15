import os.path
from datetime import datetime

from CFS.Data import hardcoded


class Backup:
    # This class is used to back up flight data to a csv file

    def __init__(self, file="untitled", path=hardcoded.BACKUPS_PATH):
        # This function is used to initialise and start the backup process
        # String    path    Used to get file path for maintained data or use default

        # Start logger (Currently not needed)
        # self.__logger = logging.getLogger("Maintained Data")
        # self.__logger.info("Started Maintained Data Logger.")

        # File
        date = datetime.now().strftime("-%Y_%m_%d-%I_%M_%S_%p")
        self.__PATH = path + file + date + ".csv"

        self.__file = open(self.__PATH, "a")

    def write(self, line):
        # This function will put the line into the csv file
        # String    line    Line of data to store

        # TODO: Validation of line

        self.__file.write(line + "\n")
        os.fsync(self.__file)

    def stop(self):
        # This function is used to close the file
        self.__file.close()
