import datetime
import logging
import os
import threading
import time

from CFS.Data import hardcoded
from picamera import PiCamera


# Get timestamp HH-MM-SS
def get_timestamp():
    ut = time.time()
    return datetime.datetime.fromtimestamp(ut).strftime('%H-%M-%S')


# Get datestamp YYYY-mm-dd
def get_datestamp():
    ut = time.time()
    return datetime.datetime.fromtimestamp(ut).strftime('%Y-%m-%d')


def get_path():
    # Used to get path to a date stamped directory
    datestamp = get_datestamp()

    # Find unique file id
    path = hardcoded.CAMERA_PATH + datestamp
    count = 0
    while os.path.isdir(path):
        count += 1
        path = hardcoded.CAMERA_PATH + datestamp + '_{}'.format(count)

    os.mkdir(path)  # Create directory
    return path


class Camera:
    # This class is used to get camera footage

    def __init__(self):
        # Used to initialise the PiCamera object and file structure

        # Start logger
        self._logger = logging.getLogger("Camera")
        self._logger.info("Started Camera Logger.")

        # Initialise the camera
        self.__camera = PiCamera()
        self.__camera.resolution = hardcoded.RESOLUTION
        self.__camera.framerate = hardcoded.FRAMERATE
        self.__camera.exposure_mode = 'sports'

        self.__segment = 0  # Stores current camera segment

        self._logger.info("Initialised and setup PiCamera object")

        # Setting up path and threading
        self.__path = get_path()  # Setup file path
        self._logger.info("Camera footage stored in {}".format(self.__path))

        self.__activation = False  # Activation variable
        self.__thread = None  # Stores thread so we can perform health checks

        self.__failed = 0

    def activate(self):
        # Used to activate the camera
        # TODO: Return error codes?
        if not self.__activation:
            self._logger.info("Activating Camera Sensor")
            self.__activation = True

            self.__thread = threading.Thread(target=self.__record, name='camera')
            self.__thread.start()

        elif not self.__thread.is_alive():
            self._logger.warning("Camera Sensor thread is dead, reviving")
            self.__thread = threading.Thread(target=self.__record, name='camera')
            self.__thread.start()

        else:
            self._logger.error("Camera Sensor thread is already active")

    def deactivate(self):
        # Used to stop the camera
        self._logger.info("Stopping Camera")
        self.__activation = False

    def is_activated(self):
        if self.__activation:
            return self.__thread.is_alive()
        else:
            return False

    def __get_file(self):
        # Used to get incrementing file names
        self.__segment += 1  # Increment segment number
        return '{}/seg_{}.h264'.format(self.__path, self.__segment)  # Get file name

    def __record(self):
        # This is a threaded function to record video
        try:
            self._logger.info("Camera recording start seg {}".format(self.__segment))

            self.__camera.start_recording(self.__get_file())  # Record segment
            self.__camera.wait_recording(hardcoded.SEG_LENGTH)
            while self.__activation:
                self.__camera.split_recording(self.__get_file())
                self.__camera.wait_recording(hardcoded.SEG_LENGTH)
            self.__camera.stop_recording()

            self._logger.info("Camera recording stop seg {}".format(self.__segment))
        except:
            self._logger.info("Camera recording failed seg {}".format(self.__segment))
            self.__failed += 1
            self.__activation = False
