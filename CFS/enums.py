from enum import unique, Enum

from CFS.Data import hardcoded


@unique
class ContainerStates(int, Enum):
    # This class is an Enum used to store the mapping between state and id
    LAUNCH_WAIT = 1
    ASCENT = 2
    ROCKET_SEPARATION = 3
    DESCENT = 4
    TP_RELEASE = 5
    LANDED = 6

    def __repr__(self):
        return self.value


@unique
class PayloadStates(int, Enum):
    # This class is an Enum used to store the mapping between state and id
    LAUNCH_STANDBY = 1
    STANDBY = 2
    RELEASED = 3
    STABILISE = 4
    LANDED = 5

    def __repr__(self):
        return self.value

@unique
class MaintainedKeys(str, Enum):
    # This class is an Enum used to store maintained data keys
    MISSION_START_TIME = "mission_start_time"
    PACKET_COUNT = "packet_count"
    PACKET_COUNT_X = "packet_count_x"
    CONTAINER_STATE = "container_state"
    PAYLOAD_STATE = "payload_state"
    LAUNCH_ALT = "launch_alt"
    CMD_ECHO = "cmd_echo"
    CX_TX = "transmit_flag"

    @classmethod
    def check_value_exists(cls, value):
        # Used to check if a value exists
        return value in (val.value for val in cls.__members__.values())


@unique
class XBeeAddress(str, Enum):
    # This class is an Enum used to identify XBees
    CONTAINER = hardcoded.XBEE_CONTAINER
    PAYLOAD = hardcoded.XBEE_PAYLOAD
    GROUND = hardcoded.XBEE_GROUND