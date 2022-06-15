import sys
import RPi.GPIO as GPIO
import time

triggerPIN = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(triggerPIN,GPIO.OUT)
GPIO.setwarnings(False)

buzzer = GPIO.PWM(triggerPIN, 2700) # Set frequency to 1 Khz
buzzer.start(50) # Set dutycycle to 10
time.sleep(1)
GPIO.cleanup()
sys.exit()
