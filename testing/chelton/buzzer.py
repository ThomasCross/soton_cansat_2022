import time
import RPi.GPIO as GPIO

from CFS.Mechanisms.buzzer import BuzzerMech

buzzer = BuzzerMech()

buzzer.sound_init()

time.sleep(2)

buzzer.activate()

time.sleep(5)

buzzer.disable()

GPIO.cleanup()


