import threading

from CFS.Sensors.sensor import Sensor, SensorIDs
import smbus
from time import sleep

class Air_Pressure(Sensor):
    # ID: 1
    # Type: Air Pressure
    # Model: MS563702BA03-50

    # Comm Method: I2C
    # I2C Device Address: 0x76(118)

    override_flag = False  # Stores flag used to enable/disable simulation override

    # TODO: Hard coded values for air pressure

    def __init__(self, i2c):
        # Initialises Air Pressure sensor class, passes type and ID to super class.
        super().__init__("Air_Pressure", SensorIDs.PRESSURE)

        self.__i2c = i2c
        self.__override_data = 1013.25

        self.__pressure = 1013.25
        self.__temp = 20

        self.__lock = threading.Lock()

        threading.Thread(target=self.sensor_data, name='pressure_data').start()

    def start_override(self):
        # Used to enable simulation mode, using the override flag
        self.override_flag = True

    def stop_override(self):
        # Used to disable simulation mode, using the override flag
        self.override_flag = False

    def sensor_init(self):
        # 0x1E(30) Reset command
        self.__i2c.write_byte(0x76, 0x1E)
        sleep(0.01)

        # Read 12 bytes of calibration data
        # Read pressure sensitivity
        data = self.__i2c.read_i2c_block_data(0x76, 0xA2, 2)
        self.__pressure_sensitivity = data[0] * 256 + data[1]

        # Read pressure offset
        data = self.__i2c.read_i2c_block_data(0x76, 0xA4, 2)
        self.__pressure_offset = data[0] * 256 + data[1]

        # Read temperature coefficient of pressure sensitivity
        data = self.__i2c.read_i2c_block_data(0x76, 0xA6, 2)
        self.__temp_coefficient_sensitivity = data[0] * 256 + data[1]

        # Read temperature coefficient of pressure offset
        data = self.__i2c.read_i2c_block_data(0x76, 0xA8, 2)
        self.__temp_coefficient_offset = data[0] * 256 + data[1]

        # Read reference temperature
        data = self.__i2c.read_i2c_block_data(0x76, 0xAA, 2)
        self.__temp_ref = data[0] * 256 + data[1]

        # Read temperature coefficient of the temperature
        data = self.__i2c.read_i2c_block_data(0x76, 0xAC, 2)
        self.__temp_coefficient_temp = data[0] * 256 + data[1]

        # 0x40(64)	Pressure conversion(OSR = 256) command
        self.__i2c.write_byte(0x76, 0x40)
        sleep(0.01)

        # Read digital pressure value
        # Read data back from 0x00(0), 3 bytes
        # D1 MSB2, D1 MSB1, D1 LSB
        value = self.__i2c.read_i2c_block_data(0x76, 0x00, 3)
        self.__d1 = value[0] * 65536 + value[1] * 256 + value[2]

        # 0x50(64)	Temperature conversion(OSR = 256) command
        self.__i2c.write_byte(0x76, 0x50)
        sleep(0.01)

    def sensor_data(self):
        while True:
            self.sensor_init()

            value = self.__i2c.read_i2c_block_data(0x76, 0x00, 3)
            d2 = value[0] * 65536 + value[1] * 256 + value[2]

            dT = d2 - self.__temp_ref * 256
            temp = 2000 + dT * self.__temp_coefficient_temp / 8388608
            off = self.__pressure_offset * 131072 + (self.__temp_coefficient_offset * dT) / 64
            sens = self.__pressure_sensitivity * 65536 + (self.__temp_coefficient_sensitivity * dT) / 128
            t2 = 0
            off2 = 0
            sens2 = 0

            if temp > 2000:
                t2 = 5 * dT * dT / 274877906944
                off2 = 0
                sens2 = 0

            elif temp < 2000:
                t2 = 3 * (dT * dT) / 8589934592
                off2 = 61 * ((temp - 2000) * (temp - 2000)) / 16
                sens2 = 29 * ((temp - 2000) * (temp - 2000)) / 16

                if temp < -1500:
                    off2 = off2 + 17 * ((temp + 1500) * (temp + 1500))
                    sens2 = sens2 + 9 * ((temp + 1500) * (temp + 1500))

            temp = temp - t2
            off = off - off2
            sens = sens - sens2

            pressure = ((((self.__d1 * sens) / 2097152) - off) / 32768.0) / 100.0
            cTemp = temp / 100.0

            self.__pressure = pressure
            self.__temp = cTemp

            sleep(0.5)

    def get_data(self):
        # Used to get data from the air pressure sensor or simulation

        if self.override_flag:
            return self.__override_data

        else:
            # Ask Oli I have no bloody clue what this does
            return self.__pressure

    def get_temp(self):
        # Ask Oli I have no bloody clue what this does
        return self.__temp

    def input_sim_data(self, value):
        # This is used to input simulation data
        self.__override_data = value
