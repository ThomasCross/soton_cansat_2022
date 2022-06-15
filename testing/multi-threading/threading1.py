#!/usr/bin/python

import datetime
import os
from picamera import PiCamera
import threading
import time

class timeThread (threading.Thread):
    def __init__  (self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.loop = True

    def run (self):
        print("Starting " + self.name)

        while self.loop:
            time.sleep(1)
            print("{}: Time - {}".format(self.name, time.ctime(time.time())))

    def stop (self):
        self.loop = False

class tempThread (threading.Thread):
    def __init__ (self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.finished = False

    def run (self):
        print("Starting " + self.name)

        for i in range (0, 10):
            print("{}: Starting {}".format(self.name, i))
            time.sleep(1)

        print("Finishing " + self.name)
        self.finished = True

    def finished (self):
        return self.finished

class cameraThread (threading.Thread):
    def __init__ (self, threadID, name, dir, res, fps, no_seg, len_seg):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.dir = dir
        self.res = res
        self.fps = fps
        self.no_seg = no_seg
        self.len_seg = len_seg
        self.finished = False

    def run (self):
        print("Starting " + self.name)

        camera = PiCamera()
        camera.resolution = self.res
        camera.framerate = self.fps
        camera.exposure_mode = 'sports'

        print("{}: Storing footage in {}".format(self.name, self.dir))

        for i in range(self.no_seg):
            file = '{}/seq{}.h264'.format(self.dir, get_timestamp())
            print("{}: Starting {} {}/{}".format(self.name, file, i, no_seg))
            camera.start_recording(file)
            time.sleep(self.len_seg)
            camera.stop_recording()

        print("Finishing " + self.name)
        self.finished = True

    def get_timestamp():
	    ut = time.time()
	    return datetime.datetime.fromtimestamp(ut).strftime('%H-%M-%S')

    def finished (self):
        return self.finished

threads = []

timeTrd = timeThread(1, "time-thread")
#cameraTrd = cameraThread(2, "camera-thread", "/var/www/html/testing/", (1280,720), 30, 12, 10)
cameraTrd = tempThread(2, "camera-temp-thread")

timeTrd.start()
cameraTrd.start()

threads.append(timeTrd)
threads.append(cameraTrd)

while True:
    time.sleep(1)
    if cameraTrd.finished:
        cameraTrd.join()
        timeTrd.stop()
        timeTrd.join()
        break

print("Total Finish")
