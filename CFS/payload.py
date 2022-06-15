import logging
import time
from datetime import datetime

import board
import smbus
from digitalio import DigitalInOut

from CFS.Comms.xbee import Xbee
from CFS.Data import hardcoded
from CFS.Data.backups import Backup
from CFS.Data.logger import setup_logging
from CFS.Data.maintained import MaintainedData, MaintainedKeys
from CFS.Listeners.listener import Listener
from CFS.Listeners.xbeelistener import XbeeListener
from CFS.Mechanisms.stabilisation import StabilisationMech
from CFS.Sensors.airpressure import Air_Pressure
from CFS.Sensors.camera import Camera
from CFS.Sensors.healthchecks import HealthChecks
from CFS.Sensors.rotation import Rotation
from CFS.Sensors.voltage import Voltage
from CFS.enums import PayloadStates, XBeeAddress, ContainerStates


class Payload:

    def __init__(self):
        # Initialise Logger
        setup_logging("payload")
        self.__logger = logging.getLogger("Payload")
        self.__logger.info("Started Payload Logger")

        # Initialise Data Objects
        self.__data_maintained = MaintainedData()  # Set to default maintained file path
        self.__data_backups = Backup("payload")  # Set to default path, custom file name

        self.__hardware = PayloadHardware(self.__logger)

        # Health Checks and Boot
        self.__boot_message()
        self.__health_message()

        self.__running = True

        # Get and set initial height
        self.__data_maintained.write_value(MaintainedKeys.LAUNCH_ALT, self.get_height(False))

        # XBee Receiver Listeners
        if self.__hardware.xbee is not None:
            self.__hardware.xbee.add_listener(
                XbeeListener(self.receiver_thread)
            )

        # Camera Listener
        self.__data_maintained.add_listener_state(
            Listener(self.camera_update)
        )

        # Stabilisation Listener
        self.__data_maintained.add_listener_state(
            Listener(self.stabilisation_update)
        )

        # Container State Listener
        self.__data_maintained.add_listener_state(
            Listener(self.__state_update)
        )

        self.__state_thread()

    def __state_thread(self):
        counter = 0

        state_transmit = 0

        while self.__running:
            state = self.__data_maintained.read_value(MaintainedKeys.PAYLOAD_STATE)
            container_state = self.__data_maintained.read_value(MaintainedKeys.CONTAINER_STATE)

            if state == PayloadStates.LAUNCH_STANDBY and container_state == ContainerStates.ASCENT:
                self.__data_maintained.write_value(MaintainedKeys.PAYLOAD_STATE, PayloadStates.STANDBY)

                self.__logger.info("STATE: STANDBY")
                print("STATE: STANDBY")

            elif state == PayloadStates.STANDBY and container_state == ContainerStates.TP_RELEASE:
                self.__data_maintained.write_value(MaintainedKeys.PAYLOAD_STATE, PayloadStates.RELEASED)
                counter = 10 * 2

                self.__logger.info("STATE: RELEASED")
                print("STATE: RELEASED")

            elif state == PayloadStates.RELEASED:
                counter -= 1
                if counter <= 0:
                    self.__data_maintained.write_value(MaintainedKeys.PAYLOAD_STATE, PayloadStates.STABILISE)

                    self.__logger.info("STATE: STABILISE")
                    print("STATE: STABILISE")

            elif state == PayloadStates.STABILISE and container_state == ContainerStates.LANDED:
                self.__data_maintained.write_value(MaintainedKeys.PAYLOAD_STATE, PayloadStates.LANDED)

                self.__logger.info("STATE: LANDED")
                print("STATE: LANDED")

            if state_transmit >= 10:
                self.__state_update()
                state_transmit = -1

            state_transmit += 1

            time.sleep(0.5)

    def receiver_thread(self, address, message: str):
        # This is a function used as a thread for receiving
        split_msg = message.strip().split(',')
        try:
            if split_msg[0] == 'CMD' and int(split_msg[1]) == hardcoded.TEAM_ID:
                if split_msg[2] == 'ST':
                    self.__update_time(self.__crap_time_to_unix(split_msg[3]))

                    self.__logger.info("CMD: ST" + self.__get_time())
                    print("CMD: ST", self.__get_time())

                elif split_msg[2] == 'RST':  # Reset cansat states CMD,<TEAM ID>,RST
                    self.__perform_reset()

                    self.__logger.info("CMD: RESET")
                    print("CMD: RESET")

                elif split_msg[2] == 'HEALTH':  # Returns health message CMD,<TEAM ID>,HEALTH
                    self.__health_message()

                    self.__logger.info("CMD: SIM HEALTH")
                    print("CMD: SIM HEALTH")

                else:
                    self.__logger.warning("Received invalid command 1: {}".format(message))

            elif int(split_msg[0]) == hardcoded.TEAM_ID and split_msg[3] == 'X':
                if split_msg[4] == 'TS':
                    self.__payload_telemetry_request()

                elif split_msg[4] == 'SU':
                    if split_msg[5] == 'LAUNCH_WAIT':
                        state = ContainerStates.LAUNCH_WAIT
                    elif split_msg[5] == 'ASCENT':
                        state = ContainerStates.ASCENT
                    elif split_msg[5] == 'ROCKET_SEPARATION':
                        state = ContainerStates.ROCKET_SEPARATION
                    elif split_msg[5] == 'DESCENT':
                        state = ContainerStates.DESCENT
                    elif split_msg[5] == 'TP_RELEASE':
                        state = ContainerStates.TP_RELEASE
                    elif split_msg[5] == 'LANDED':
                        state = ContainerStates.LANDED

                    self.__data_maintained.write_value(MaintainedKeys.CONTAINER_STATE, state)

                    self.__logger.info("CMD: STATE CON: ".format(state))
                    print("CMD: STATE CON: ", split_msg[5], state)

                elif split_msg[4] == 'RST':
                    self.__perform_reset()

                    self.__logger.info("CMD: RESET CON")
                    print("CMD: RESET CON")

                else:
                    self.__logger.warning("Received invalid command 2: {}".format(message))

            else:
                self.__logger.warning("Received invalid message 3: {}".format(message))
        except Exception as e:
            self.__logger.warning("Received invalid message 4: {} | {}".format(message, e))

    def __perform_reset(self):
        self.__logger.info("Performing RESET")

        self.__data_maintained.reset()
        self.__data_backups.stop()
        self.__data_backups = Backup("payload")

        self.__running = True
        self.__boot_message()

    def __transmit(self, packet, address, type=True):
        packet_count = self.__data_maintained.read_value(
            MaintainedKeys.PACKET_COUNT if type else MaintainedKeys.PACKET_COUNT_X
        ) + 1

        packet[2] = packet_count

        self.__data_maintained.write_value(
            MaintainedKeys.PACKET_COUNT if type else MaintainedKeys.PACKET_COUNT_X
            , packet_count)

        output = ''
        for line in packet:
            output += str(line)
            output += ','

        output = output[:-1] + "\n"

        if self.__hardware.xbee is not None:
            self.__hardware.xbee.send(output, address)
            self.__logger.info("XBEE Output: " + output)

        else:
            self.__logger.info("XBEE Unavailable Error: " + output)

    def __boot_message(self):
        packet = [  # Boot Packet
            hardcoded.TEAM_ID,  # Team ID
            self.__get_mission_time(),  # Mission Time
            -1,  # Packet Count
            'X',  # Packet Type
            'BP',  # Other Packet Type: Boot Payload
        ]

        self.__transmit(packet, XBeeAddress.GROUND, False)

    def __health_message(self):
        packet = [  # Boot Packet
            hardcoded.TEAM_ID,  # Team ID
            self.__get_mission_time(),  # Mission Time
            -1,  # Packet Count
            'X',  # Packet Type
            'HCP',  # Other Packet Type: Health Check Payload
            "{:.2f}".format(self.__hardware.pi.get_temp()),
            "{:.2f}".format(self.__hardware.pi.get_load()),
            "{:.2f}".format(self.__hardware.pi.get_disk())
        ]

        self.__transmit(packet, XBeeAddress.GROUND, False)

    def __state_update(self):
        packet = [  # Payload State Update Packet
            hardcoded.TEAM_ID,  # Team ID
            self.__get_mission_time(),  # Mission Time
            -1,  # Packet Count
            'X',  # Packet Type
            'SU',  # Other Packet Type: State Update
            self.__data_maintained.read_value(MaintainedKeys.PAYLOAD_STATE)
        ]

        self.__transmit(packet, XBeeAddress.CONTAINER, False)

    def __payload_telemetry_request(self):
        imu = self.__hardware.rotation.get_data()
        # [accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z, mag_x, mag_y, mag_z, yaw_angle]
        accel_x = imu[0]  # roll
        accel_y = imu[1]  # pitch
        accel_z = imu[2]  # yaw
        gyro_x = imu[3]
        gyro_y = imu[4]
        gyro_z = imu[5]
        mag_x = imu[6]
        mag_y = imu[7]
        mag_z = imu[8]
        yaw_pointing_error = imu[9]

        # [TODO] move stepper by yaw_pointing_error
        # Use stabilisation.get_pos for stepper position

        payload_state = self.__data_maintained.read_value(MaintainedKeys.PAYLOAD_STATE)

        if payload_state == PayloadStates.LAUNCH_STANDBY:
            state = 'LAUNCH_STANDBY'
        elif payload_state == PayloadStates.STANDBY:
            state = 'STANDBY'
        elif payload_state == PayloadStates.RELEASED:
            state = 'RELEASED'
        elif payload_state == PayloadStates.STABILISE:
            state = 'STABILISE'
        elif payload_state == PayloadStates.LANDED:
            state = 'LANDED'

        packet = [  # Payload Request Packet
            hardcoded.TEAM_ID,  # Team ID
            self.__get_mission_time(),  # Mission Time
            -1,  # Packet Count
            'X',  # Packet Type
            'TR',  # Other Packet Type: Telemetry Response
            "{:.1f}".format(self.get_height()),
            "{:.1f}".format(self.__hardware.air_pressure.get_temp()),
            "{:.2f}".format(self.__hardware.voltage.get_data()),
            gyro_x,
            gyro_y,
            gyro_z,
            accel_x,
            accel_y,
            accel_z,
            mag_x,
            mag_y,
            mag_z,
            yaw_pointing_error,  # hopefully -20 < angle < 20 deg
            state
        ]

        self.__transmit(packet, XBeeAddress.CONTAINER, False)

    def camera_update(self):
        # This is a function called by the camera listener on state updates
        state = self.__data_maintained.read_value(MaintainedKeys.PAYLOAD_STATE)

        if self.__hardware.camera is not None:
            if PayloadStates.STANDBY <= state < PayloadStates.LANDED:
                if not self.__hardware.camera.is_activated():
                    self.__hardware.camera.activate()
            else:
                self.__hardware.camera.deactivate()

    def stabilisation_update(self):
        # This is a function called by the stabilisation listener on state updates
        state = self.__data_maintained.read_value(MaintainedKeys.PAYLOAD_STATE)

        if PayloadStates.STABILISE <= state < PayloadStates.LANDED:
            if not self.__hardware.stabilisation.is_activated():
                self.__hardware.stabilisation.activate()
        else:
            self.__hardware.stabilisation.disable()

    def get_height(self, offset=True):
        # This function is used to poll the pressure and temperature sensor to get altitude
        pressure = self.__hardware.air_pressure.get_data() * 100  # in Pa
        temp = self.__hardware.air_pressure.get_temp() + 273.15  # in Kelvin

        pressure_sea_level = 101325  # in Pa

        # Derived from Hypsometric Formula
        altitude = ((((pressure_sea_level / pressure) ** (1 / 5.257)) - 1) * temp) / 0.0065

        if offset:
            altitude -= self.__data_maintained.read_value(MaintainedKeys.LAUNCH_ALT)

        return float("{:.2f}".format(altitude))

    def __crap_time_to_unix(self, time):
        base = 1654383600

        split_time = time.split(":")

        return base + (3600 * int(split_time[0])) + (60 * int(split_time[1])) + int(split_time[2])

    def __update_time(self, unix):
        clk_id = time.CLOCK_REALTIME
        time.clock_settime(clk_id, float(unix))

    def __get_time(self):
        return datetime.fromtimestamp(time.time()).strftime('%H:%M:%S')

    def __get_mission_time(self):
        return datetime.fromtimestamp(time.time()).strftime('%H:%M:%S')


class PayloadHardware:
    def __init__(self, logger):
        self.__i2c = board.I2C()
        self.__bus = smbus.SMBus(1)

        self.__scl = board.SCL
        self.__sda = board.SDA
        self.__reset_pin = DigitalInOut(board.D5)

        # Health Checks
        self.pi = HealthChecks()

        # Comms
        try:
            self.xbee = Xbee()
        except:
            print("ERROR Unable to start XBee")
            logger.error("ERROR Unable to start XBee")
            self.xbee = None

        # Sensors
        self.air_pressure = Air_Pressure(self.__bus)
        self.voltage = Voltage()
        self.rotation = Rotation(self.__scl, self.__sda, self.__reset_pin)

        # Camera
        try:
            self.camera = Camera()
        except:
            print("ERROR Unable to start Camera")
            logger.error("ERROR Unable to start Camera")
            self.camera = None

        # Mechanisms
        self.stabilisation = StabilisationMech()
