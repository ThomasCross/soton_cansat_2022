import logging

from abc import abstractmethod
from enum import unique, Enum


class Mechanism:
    # This class is an 'abstract' class used to help define our servo mechanism classes.

    def __init__(self, mechanism_name, mechanism_id):
        # Used to initialise Mechanism class
        # String    mechanism_name     Contains name of sensor
        # Int       mechanism_id       Contains id of sensor

        # Start logger
        self._logger = logging.getLogger("Mechanism({})".format(mechanism_name))
        self._logger.info("Started Mechanism Logger.")

        self.__mechanism_name = mechanism_name
        self.__mechanism_id = mechanism_id

    @property
    def get_mechanism_name(self):
        # Used to return mechanism_name, disallows editing/readonly
        return self.__mechanism_name

    @property
    def get_mechanism_id(self):
        # Used to return mechanism_id, disallows editing/readonly
        return self.__mechanism_id

    @abstractmethod
    def activate(self):
        # This is an abstract method to activate a mechanism
        pass


def get_mechanism(mechanisms: list[Mechanism], mech_id: int):
    # This is a static function used to return a certain mechanism from a list
    for m in mechanisms:
        if m.get_mechanism_id == mech_id:
            return m

    return None


@unique
class MechanismIDs(int, Enum):
    # This class is an Enum used to store the mapping between mechanism and id
    PARACHUTE = 1
    PAYLOAD = 2
    STABILISATION = 3
    BUZZER = 4
