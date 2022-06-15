import time

from CFS.Data.logger import setup_logging
from CFS.Sensors.camera import Camera

setup_logging("camera_test")

camera = Camera()

print("Starting Section A")
camera.activate()
time.sleep(11)
camera.deactivate()
print("Stopping Section A")

time.sleep(10)

print("Starting Section B")
camera.activate()
time.sleep(5)
camera.deactivate()
print("Stopping Section B")