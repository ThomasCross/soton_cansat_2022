# This will make a 10 second video using the Raspberry Pi Camera
from time import sleep
from picamera import PiCamera

camera = PiCamera(
	resolution=(1280, 720),
	framerate=30,
)
camera.exposure_mode = 'sports'

camera.start_recording('/var/www/html/testing/python_video/video.h264')
sleep(5)
camera.stop_recording()
