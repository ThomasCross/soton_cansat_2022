from CFS.Sensors.sensor import Sensor, SensorIDs
import time
import busio
import math
import adafruit_bno08x
from adafruit_bno08x import (
    BNO_REPORT_GYROSCOPE,
    BNO_REPORT_MAGNETOMETER,
    BNO_REPORT_ROTATION_VECTOR,
)
from adafruit_bno08x.i2c import BNO08X_I2C


class Rotation(Sensor):
    # ID: 5
    # Type: IMU
    # Model: BNO085

    # Comm Method: I2C
    # I2C Device Address (Handled by library)

    device = None
    prev_angle = 0

    def __init__(self, scl, sda, reset_pin):
        # Initialises Temperature sensor class, passes type and ID to super class.
        # i2c is board 'i2c = board.I2C()'
        super().__init__("Temperature", SensorIDs.TEMPERATURE)

        self.device = BNO08X_I2C(busio.I2C(scl, sda), reset=reset_pin, debug=False)

        self.device = BNO08X_I2C(busio.I2C(scl, sda, frequency=400000))

        self.device.enable_feature(BNO_REPORT_GYROSCOPE)
        self.device.enable_feature(BNO_REPORT_MAGNETOMETER)
        self.device.enable_feature(BNO_REPORT_ROTATION_VECTOR)

        self.prev_angle = self.get_data()[9]

    def get_data(self):
        # Used to get data from the temperature sensor

        try:
            accel_x, accel_y, accel_z = 0, 0, 0
            gyro_x, gyro_y, gyro_z = self.device.gyro
            mag_x, mag_y, mag_z = self.device.magnetic
            quat_i, quat_j, quat_k, quat_real = self.device.quaternion

            # roll (x-axis rotation)
            #sinr_cosp = 2 * (quat_real * quat_i + quat_j * quat_k)
            #cosr_cosp = 1 - 2 * (quat_i * quat_i + quat_j * quat_j)
            #roll = math.atan2(sinr_cosp, cosr_cosp)

            #pitch (y-axis rotation)
            #sinp = 2 * (quat_real * quat_j - quat_k * quat_i)
            #if (abs(sinp) >= 1):
                #pitch = math.copysign(math.pi / 2, sinp) #use 90 degrees if out of range
            #else:
                #pitch = math.asin(sinp)

            #yaw (z-axis rotation)
            siny_cosp = 2 * (quat_real * quat_k + quat_i * quat_j)
            cosy_cosp = 1 - 2 * (quat_j * quat_j + quat_k * quat_k)
            yaw = math.atan2(siny_cosp, cosy_cosp)
            yaw = math.degrees(yaw)
            yaw = float("{:.1f}".format(yaw))

            return [accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z, mag_x, mag_y, mag_z, yaw]

        except:
            return [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1]


