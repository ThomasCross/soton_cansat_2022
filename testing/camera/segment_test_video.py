# This will make a series of timestamped video clips
import datetime
import os
from picamera import PiCamera
import time
from time import sleep

VIDEO_DIR = '/var/www/html/testing/python_video/'
RESOLUTION = (1280, 720)
FRAMERATE = 30

SEGMENTS = 12
LENGTH = 600


# Get folder name for video segments
def get_folder():
    ut = time.time()
    datestamp = datetime.datetime.fromtimestamp(ut).strftime('%Y-%m-%d')
    folder = datestamp

    count = 0
    while os.path.isdir(VIDEO_DIR + folder):
        count += 1
        folder = datestamp + '_{}'.format(count)

    os.mkdir(VIDEO_DIR + folder)
    return folder


# Get timestamp HH-MM-SS
def get_timestamp():
    ut = time.time()
    return datetime.datetime.fromtimestamp(ut).strftime('%H-%M-%S')


# Init PiCamera with settings
camera = PiCamera()
camera.resolution = RESOLUTION
camera.framerate = FRAMERATE
camera.exposure_mode = 'sports'

# Get segments of video
folder = get_folder()
print('Starting camera, footage stored in {}{}'.format(VIDEO_DIR, folder))

for x in range(SEGMENTS):
    file = '{}{}/seq{}.h264'.format(VIDEO_DIR, folder, get_timestamp())
    print('Starting {} {}/{}'.format(file, x, SEGMENTS))
    camera.start_recording(file)
    sleep(LENGTH)
    camera.stop_recording()
