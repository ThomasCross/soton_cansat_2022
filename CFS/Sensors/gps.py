import logging
import threading
import time

from CFS.Sensors.sensor import Sensor, SensorIDs
import pynmea2


class GPS(Sensor):
    # ID: 3
    # Type: GPS

    # Comm Method: I2C
    # I2C Device Address  0x42

    def __init__(self, i2c):
        # Initialises Temperature sensor class, passes type and ID to super class.
        # i2c is board 'i2c = board.I2C()'
        super().__init__("GPS", SensorIDs.GPS)

        self.__i2c = i2c
        self.__address = 0x42
        self.__gpsReadInterval = 0.1

        self.__activation = False
        self.__thread = None

        self.__timestamp = '00:00:00'
        self.__lat = 0
        self.__long = 0
        self.__no_sat = 0
        self.__alt = 0

        self._logger = logging.getLogger("Sensor(GPS Specific)")
        self._logger.info("Started Sensor GPS Logger.")

    def get_data(self):
        return [self.__timestamp, self.__lat, self.__long, self.__alt, self.__no_sat]

    def activate(self):
        # Used to activate the GPS
        if not self.__activation:
            self._logger.info("Activating GPS Sensor")
            self.__activation = True

            self.__thread = threading.Thread(target=self.__runGPS, name='gps')
            self.__thread.start()

        elif not self.__thread.is_alive():
            self._logger.warning("GPS Sensor thread is dead, reviving")
            self.__thread = threading.Thread(target=self.__runGPS, name='gps')
            self.__thread.start()

        else:
            self._logger.error("GPS Sensor thread is already active")

    def deactivate(self):
        # Used to stop the GPS
        self._logger.info("Stopping GPS")
        self.__activation = False

    def is_activated(self):
        return self.__thread.is_alive()

    def __runGPS(self):
        while self.__activation:
            self.__readGPS()
            time.sleep(self.__gpsReadInterval)

    def __readGPS(self):
        c = None
        response = []
        while True:
            c = self.__i2c.read_byte(self.__address)
            if c == 255:
                return False
            elif c == 10:
                break
            else:
                response.append(c)

        gpsChars = ''.join(chr(c) for c in response)

        try:
            msg = pynmea2.parse(gpsChars)

            if hasattr(msg, 'timestamp'):
                temp = msg.timestamp
                if temp is not None:
                    self.__timestamp = temp

            if hasattr(msg, 'latitude'):
                temp = msg.latitude
                if temp is not None:
                    self.__lat = "{:.4f}".format(temp)

            if hasattr(msg, 'longitude'):
                temp = msg.longitude
                if temp is not None:
                    self.__long = "{:.4f}".format(temp)

            if hasattr(msg, 'num_sats'):
                temp = msg.num_sats
                if temp is not None:
                    self.__no_sat = str(int(temp))

            if hasattr(msg, 'altitude'):
                temp = msg.altitude
                if temp is not None:
                    self.__alt = "{:.1f}".format(temp)

            #self._logger.info("Passer: {}".format(repr(msg)))
        except pynmea2.ParseError as e:
            #self._logger.error("Passer ERROR: {}".format(e))
            pass
