import time

from abc import abstractmethod
from CFS.Mechanisms.mechanism import Mechanism
from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory


class ServoMechanism(Mechanism):
    # This class is used to define servo mechanisms

    def __init__(self, mechanism_name, mechanism_id, servo_pin):
        # Used to initialise ServoMechanism class
        # String    mechanism_name     Contains name of sensor
        # Int       mechanism_id       Contains id of sensor
        # Int       servo_pin          Pin of servo mechanism

        super().__init__(mechanism_name, mechanism_id)

        self._logger.info("Starting Servo Mechanism Object Pin: {}".format(servo_pin))

        myCorrection = 0.45
        maxPW = (2.0 + myCorrection) / 1000
        minPW = (1.0 - myCorrection) / 1000

        factory = PiGPIOFactory()

        self.__servo = Servo(servo_pin, min_pulse_width=minPW, max_pulse_width=maxPW, pin_factory=factory)

    def _set_servo_pos(self, pos):
        # Used to set servo to a position and validate position change
        if abs(pos) > 1:
            self._logger.error("Servo position {} invalid.".format(pos))
        else:
            self.__servo.value = pos
            time.sleep(0.5)
            self.__servo.detach()

    def set_servo_pos(self, pos):
        self._set_servo_pos(pos)

    @abstractmethod
    def activate(self):
        # This is an abstract method to activate a mechanism
        pass
