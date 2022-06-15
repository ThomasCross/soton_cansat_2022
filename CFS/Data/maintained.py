import json
import logging
import os.path
import time

from CFS.Data import hardcoded
from CFS.enums import MaintainedKeys, ContainerStates, PayloadStates
from CFS.Listeners.listener import Listener


class MaintainedData:
    # This class is used to update and read maintained data

    def __init__(self, path=hardcoded.MAINTAINED_FILE):
        # This function is used to initialise and populate the MaintainedData Object
        # String    path    Used to get file path for maintained data or use default

        # Start logger
        self.__logger = logging.getLogger("Maintained Data")
        self.__logger.info("Started Maintained Data Logger.")

        self.__data = {}
        self.__PATH = path
        self.__logger.info("Path set to: {}".format(self.__PATH))

        # Init Listener Lists
        self.__listeners_state = []

        # Check if maintained data file already exists
        if os.path.exists(self.__PATH):
            self.__read()
            if len(self.__data) != len(MaintainedKeys):  # Check to see if we have loaded the correct number of keys
                self.__logger.error("Invalid number of keys obtained from maintained data file.")
                self.reset()
        else:
            self.__logger.debug("Maintained data file does not exist, creating new file and data.")
            self.reset()

    def reset(self):
        # This function is used to reset the maintained data file and object
        self.__logger.debug("Data reset.")
        self.__data = {
            MaintainedKeys.MISSION_START_TIME: time.time(),
            MaintainedKeys.PACKET_COUNT: 0,
            MaintainedKeys.PACKET_COUNT_X: 0,
            MaintainedKeys.CONTAINER_STATE: ContainerStates.LAUNCH_WAIT,
            MaintainedKeys.PAYLOAD_STATE: PayloadStates.LAUNCH_STANDBY,
            MaintainedKeys.LAUNCH_ALT: 0,
            MaintainedKeys.CMD_ECHO: "",
            MaintainedKeys.CX_TX: False
        }
        self.__write()
        self.__notify_listener_state()

    def __write(self):
        # This is private function is used to update the maintained data file from program data
        json_output = json.dumps(self.__data)

        try:
            with open(self.__PATH, "w") as file:
                file.write(json_output)
                os.fsync(file)
                file.close()
        except IOError:
            # TODO: IO Error process
            pass

    def write_value(self, key, value):
        # This function is used to update a key value pair in the maintained data
        # MaintainedKeys    key     Used to identify value to change
        #                   value   Contains value to update with

        if MaintainedKeys.check_value_exists(key):

            if self.__data[key] != value:
                self.__logger.debug("Modifying data Key: {} Value: {}".format(key, value))
                self.__data[key] = value
                self.__write()

                # Notify listeners for certain keys
                if key == MaintainedKeys.CONTAINER_STATE or key == MaintainedKeys.PAYLOAD_STATE:
                    self.__notify_listener_state()
            else:
                self.__logger.debug("Data value same Key: {} Value: {}".format(key, value))
        else:
            self.__logger.error("Invalid MaintainedKeys Enum (write): {}".format(key))

    def __read(self):
        # This is private function is used to refresh maintained data from file
        try:
            with open(self.__PATH, "r") as file:
                json_input = file.read()
                file.close()
        except IOError:
            # TODO: IO Error process
            pass

        self.__data = json.loads(json_input)

    def read_value(self, key, file=False):
        # This function is used to read and return a singular value of maintained data
        # MaintainedKeys    key     Used to identify value to return
        # Boolean           file    Flag to refresh data from file

        if MaintainedKeys.check_value_exists(key):
            if file:
                self.__read()

            return self.__data[key]
        else:
            self.__logger.error("Invalid MaintainedKeys Enum (read): {}".format(key))

    def add_listener_state(self, listener: Listener):
        # Add state listener
        self.__listeners_state.append(listener)

    def remove_listener_state(self, listener: Listener):
        # Remove state listener
        self.__listeners_state.remove(listener)

    def __notify_listener_state(self):
        # Notify state listeners
        for listener in self.__listeners_state:
            listener.notify()
