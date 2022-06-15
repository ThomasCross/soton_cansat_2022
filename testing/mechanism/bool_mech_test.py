import time

from CFS.Data.logger import setup_logging
from CFS.Mechanisms.boolmechanism import BoolMechanism


class BoolMechTest(BoolMechanism):
    # This class is used to store and define the parachute release mechanism

    def __init__(self, servo_pin, initial_pos, activation_pos):
        # This is used to initialise the parachute release mechanism
        super().__init__("BoolMechTest", 1, servo_pin, initial_pos, activation_pos)


# Init logging, comment out line to stop logging
setup_logging("bool_mech_testing")

# Set this value to the pin used for testing
SERVO_PIN = 0

# Set these values to initial servo position and position from activation.
INITIAL_POS = 0
ACTIVATION_POS = 1

# This test code should:-
# 1. initialise the object
# 2. Move servo to initial position
# 3. Wait 5 seconds
# 4. Move servo to activation position
test_object = BoolMechTest(SERVO_PIN, INITIAL_POS, ACTIVATION_POS)
time.sleep(5)
test_object.activate()
