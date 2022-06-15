import time

from CFS.Mechanisms.parachute import ParachuteRelease

servo = ParachuteRelease()

input()
servo.activate()

time.sleep(1)
