import threading
import time

from CFS.Data import hardcoded
from CFS.Mechanisms.mechanism import Mechanism, MechanismIDs
import RPi.GPIO as GPIO


class BuzzerMech(Mechanism):
    # This class is used to store and define the buzzer mechanism

    def __init__(self):
        # This is used to initialise the buzzer mechanism
        super().__init__("BuzzerMech", MechanismIDs.BUZZER)

        self._logger.info("Starting Buzzer Mechanism")

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(hardcoded.BOT_PIN_Buzzer, GPIO.OUT)
        GPIO.setwarnings(False)

        self.__buzzer = GPIO.PWM(hardcoded.BOT_PIN_Buzzer, 2700)

        self.__activation = False  # Activation lock, false until payload is deployed
        self.__thread = None  # Stores thread so we can perform health checks

    def activate(self):
        # Used to activate Recovery Alert
        # TODO: Return status codes?
        if not self.__activation:
            self._logger.info("Activating Recovery Alert")
            self.__activation = True

            self.__thread = threading.Thread(target=self.__alert, name='buzzer_alert').start()

        elif not self.__thread.is_alive():
            self._logger.warning("Recovery Alert thread is dead, reviving")
            self.__thread = threading.Thread(target=self.__alert, name='buzzer_alert').start()

        else:
            self._logger.error("Recovery Alert thread is already active")

    def disable(self):
        # Used to disable recovery alert
        self._logger.info("Disabling Recovery Alert")
        self.__activation = False
        self.__buzzer.stop()

    def __alert(self):
        # Used to sound alert noise
        while self.__activation:
            self.__buzzer.start(50)
            time.sleep(1)

            self.__buzzer.stop()
            time.sleep(0.5)

    def sound_init(self):
        # Used to sound initialisation alert (Two short beeps)
        self.__buzzer.start(50)
        time.sleep(0.5)
        self.__buzzer.stop()
        time.sleep(0.5)

        self.__buzzer.start(50)
        time.sleep(0.5)
        self.__buzzer.stop()
        time.sleep(0.5)
