import logging
import threading
import time

from abc import abstractmethod
from enum import Enum, unique


class Sensor:
    # This class is an 'abstract' class used to help define our sensor classes.

    __sensor_name = ""  # This is used to store the name of sensor
    __sensor_id = -1  # This is used to store the id of sensor type

    def __init__(self, sensor_name, sensor_id):
        # Used to initialise Sensor class
        # String    sensor_name     Contains name of sensor
        # Int       sensor_id       Contains id of sensor

        # Start logger
        self._logger = logging.getLogger("Sensor({})".format(sensor_name))
        self._logger.info("Started Sensor Logger.")

        self.__sensor_name = sensor_name
        self.__sensor_id = sensor_id

    @property
    def get_sensor_name(self):
        # Used to return sensor_name, disallows editing/readonly
        return self.__sensor_name

    @property
    def get_sensor_id(self):
        # Used to return sensor_id, disallows editing/readonly
        return self.__sensor_name

    @abstractmethod
    def get_data(self):
        # This is an abstract method to return data from a given sensor
        pass


def get_sensor(sensors: list[Sensor], sense_id: int):
    # This is a static function used to return a certain mechanism from a list
    for s in sensors:
        if s.get_sensor_id == sense_id:
            return s

    return None


@unique
class SensorIDs(int, Enum):
    # This class is an Enum used to store the mapping between mechanism and id
    PRESSURE = 1
    TEMPERATURE = 2
    GPS = 3
    VOLTAGE = 4
    ROTATION = 5
