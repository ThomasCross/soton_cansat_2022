import random
import threading
import time
import RPi.GPIO as GPIO

from CFS.Data import hardcoded
from CFS.Mechanisms.mechanism import MechanismIDs, Mechanism


class StabilisationMech(Mechanism):
    # This class is used to define the stabilisation servo mechanism

    def __init__(self):
        # Used to initialise stabilisation mechanism object
        super().__init__(
            "StabilisationMech",
            MechanismIDs.STABILISATION
        )  # Initialise Parent Class

        self._logger.info("Starting Stabilisation Mechanism Object")

        self._logger.info("Setting Stabilisation Mechanism to initial position")

        self.__step_count = 4096
        # defining stepper motor sequence (found in documentation http://www.4tronix.co.uk/arduino/Stepper-Motors.php)
        self.__step_sequence = [
            [1, 0, 0, 1],
            [1, 0, 0, 0],
            [1, 1, 0, 0],
            [0, 1, 0, 0],
            [0, 1, 1, 0],
            [0, 0, 1, 0],
            [0, 0, 1, 1],
            [0, 0, 0, 1]
        ]  # magnet sequence. to move, fire the next/last output order in this sequence
        self.__motor_pins = [
            hardcoded.PAY_PIN_STABILISATION_IN1,
            hardcoded.PAY_PIN_STABILISATION_IN2,
            hardcoded.PAY_PIN_STABILISATION_IN3,
            hardcoded.PAY_PIN_STABILISATION_IN4
        ]
        self.__motor_step_counter = 0

        self.__activation = False  # Activation lock, false until payload is deployed
        self.__thread = None  # Stores thread so we can perform health checks

        # setting up
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(hardcoded.PAY_PIN_STABILISATION_IN1, GPIO.OUT)
        GPIO.setup(hardcoded.PAY_PIN_STABILISATION_IN2, GPIO.OUT)
        GPIO.setup(hardcoded.PAY_PIN_STABILISATION_IN3, GPIO.OUT)
        GPIO.setup(hardcoded.PAY_PIN_STABILISATION_IN4, GPIO.OUT)

        self.__rand_direction = 1
        self.__rand_count = 0

    def activate(self):
        # Used to activate stabilisation mechanism
        # TODO: Return status codes?
        if not self.__activation:
            self._logger.info("Activating Stabilisation Mechanism")
            self.__activation = True

            # initializing
            GPIO.output(hardcoded.PAY_PIN_STABILISATION_IN1, GPIO.LOW)
            GPIO.output(hardcoded.PAY_PIN_STABILISATION_IN2, GPIO.LOW)
            GPIO.output(hardcoded.PAY_PIN_STABILISATION_IN3, GPIO.LOW)
            GPIO.output(hardcoded.PAY_PIN_STABILISATION_IN4, GPIO.LOW)

            self.__thread = threading.Thread(target=self.__stabilisation, name='stabilisation').start()

        elif not self.__thread.is_alive():
            self._logger.warning("Stabilisation Mechanism thread is dead, reviving")

            # initializing
            GPIO.output(hardcoded.PAY_PIN_STABILISATION_IN1, GPIO.LOW)
            GPIO.output(hardcoded.PAY_PIN_STABILISATION_IN2, GPIO.LOW)
            GPIO.output(hardcoded.PAY_PIN_STABILISATION_IN3, GPIO.LOW)
            GPIO.output(hardcoded.PAY_PIN_STABILISATION_IN4, GPIO.LOW)

            self.__thread = threading.Thread(target=self.__stabilisation, name='stabilisation').start()

        else:
            self._logger.error("Stabilisation Mechanism thread is already active")

    def disable(self):
        # Used to disable stabilisation mechanism
        self._logger.info("Disabling Stabilisation Mechanism")
        self.__activation = False

        GPIO.output(hardcoded.PAY_PIN_STABILISATION_IN1, GPIO.LOW)
        GPIO.output(hardcoded.PAY_PIN_STABILISATION_IN2, GPIO.LOW)
        GPIO.output(hardcoded.PAY_PIN_STABILISATION_IN3, GPIO.LOW)
        GPIO.output(hardcoded.PAY_PIN_STABILISATION_IN4, GPIO.LOW)

    def is_activated(self):
        if self.__activation:
            return self.__thread.is_alive()
        else:
            return False

    def __stabilisation(self):  # This crack pot method actually works?!?!?
        # Used to send values to the stabilisation servo
        while self.__activation:
            if self.__rand_count <= 0:
                self.__rand_direction = random.randint(-1, 1)

                if self.__rand_direction != 0:
                    self.__rand_count = random.randint(2, 6)

            self.__rand_count -= 1

            angle = random.randint(5, 30) * self.__rand_direction

            print(angle)

            for i in range(int((abs(angle) / 360) * 4096)):  # for each stepper step in the required angle
                for pin in range(4):  # Write to each pin the required output of current step in magnet sequence
                    GPIO.output(
                        self.__motor_pins[pin],
                        self.__step_sequence[self.__motor_step_counter][pin]
                    )  # fire the next sequence of magnets

                if angle >= 0:  # If positive (i.e. clockwise)
                    self.__motor_step_counter = (self.__motor_step_counter - 1) % 8
                else:
                    self.__motor_step_counter = (self.__motor_step_counter + 1) % 8

                time.sleep(0.002)

            time.sleep(0.25)  # Sleep before next check
