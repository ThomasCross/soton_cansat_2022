import os
import threading

import board
from datetime import datetime
import logging
import time
import sched
import smbus

from CFS.Comms.xbee import Xbee, XBeeAddress
from CFS.Data import hardcoded
from CFS.Data.backups import Backup
from CFS.Data.maintained import MaintainedData, MaintainedKeys
from CFS.Data.logger import setup_logging
from CFS.Listeners.listener import Listener
from CFS.Listeners.xbeelistener import XbeeListener
from CFS.Mechanisms.buzzer import BuzzerMech
from CFS.Mechanisms.parachute import ParachuteRelease
from CFS.Mechanisms.payload import PayloadRelease
from CFS.Sensors.airpressure import Air_Pressure
from CFS.Sensors.camera import Camera
from CFS.Sensors.gps import GPS
from CFS.Sensors.healthchecks import HealthChecks
from CFS.Sensors.temperature import Temperature
from CFS.Sensors.voltage import Voltage
from CFS.enums import ContainerStates, PayloadStates


class Container:
    def __init__(self):
        # Initialise Logger
        setup_logging("container")
        self.__logger = logging.getLogger("Container")
        self.__logger.info("Started Container Logger")

        # Initialise Data Objects
        self.__data_maintained = MaintainedData()  # Set to default maintained file path
        self.__data_backups = Backup("container")  # Set to default path, custom file name

        self.__hardware = ContainerHardware(self.__logger)

        # Health Checks and Boot
        self.__boot_message()
        self.__health_message()

        self.__running = True
        self.__sim_mode = False

        # Get and set initial height
        self.__data_maintained.write_value(MaintainedKeys.LAUNCH_ALT, self.get_height(False))

        # Start Up Indicator (Sound buzzer to indicate boot)
        self.__hardware.buzzer.sound_init()

        # XBee Receiver Listeners
        if self.__hardware.xbee is not None:
            self.__hardware.xbee.add_listener(
                XbeeListener(self.receiver_thread)
            )

        # Camera State Listener
        self.__data_maintained.add_listener_state(
            Listener(self.__camera_update)
        )

        # Parachute State Listener
        self.__data_maintained.add_listener_state(
            Listener(self.__parachute_update)
        )

        # Payload State Listener
        self.__data_maintained.add_listener_state(
            Listener(self.__payload_update)
        )

        # Beacon State Listener
        self.__data_maintained.add_listener_state(
            Listener(self.__beacon_update)
        )

        # Payload State Updater Listener
        self.__data_maintained.add_listener_state(
            Listener(self.__payload_state_update)
        )

        # Main Schedulers
        telemetry_thread = threading.Thread(target=self.__container_telemetry, name='telemetry')
        telemetry_thread.start()

        self.__logger.info("Started Container")
        print("START")

        self.__state_thread()

    def __state_thread(self):
        counter = 0
        last_height = 0

        state_timer = 0

        state_transmit = 0

        while self.__running:
            state = self.__data_maintained.read_value(MaintainedKeys.CONTAINER_STATE)
            print(self.get_height())

            if state == ContainerStates.LAUNCH_WAIT:
                if self.get_height() > 50:
                    self.__data_maintained.write_value(MaintainedKeys.CONTAINER_STATE, ContainerStates.ASCENT)
                    last_height = self.get_height()
                    counter = 0

                    self.__logger.info("STATE: Ascent")
                    print("STATE: ASCENT")

            elif state == ContainerStates.ASCENT:
                temp_height = self.get_height()

                print(temp_height, " | ", last_height, " (", last_height - 5, ") ", " ", counter)

                if temp_height < last_height - 5:  # Is cansat descending
                    counter += 1

                last_height = self.get_height()

                if counter > 4:  # Been descending for over 5 seconds
                    self.__data_maintained.write_value(MaintainedKeys.CONTAINER_STATE,
                                                       ContainerStates.ROCKET_SEPARATION)

                    self.__logger.info("STATE: Separation")
                    print("STATE: SEPARATION")

            elif state == ContainerStates.ROCKET_SEPARATION:
                if self.get_height() < 400:
                    self.__data_maintained.write_value(MaintainedKeys.CONTAINER_STATE, ContainerStates.DESCENT)

                    self.__logger.info("STATE: Descent")
                    print("STATE: DESCENT")

            elif state == ContainerStates.DESCENT:
                if self.get_height() < 300:
                    self.__data_maintained.write_value(MaintainedKeys.CONTAINER_STATE, ContainerStates.TP_RELEASE)
                    threading.Thread(target=self.__payload_telemetry_request, name='payload_telemetry').start()
                    state_timer = 30 * 2  # 30-second timer

                    self.__logger.info("STATE: TP_Release")
                    print("STATE: TP_RELEASE")

            elif state == ContainerStates.TP_RELEASE:
                state_timer -= 1
                if self.get_height() < 50 and state_timer <= 0:
                    self.__data_maintained.write_value(MaintainedKeys.CONTAINER_STATE, ContainerStates.LANDED)

                    self.__logger.info("STATE: Landed")
                    print("STATE: LANDED")

            if state_transmit >= 10:
                self.__payload_state_update()
                state_transmit = -1

            state_transmit += 1

            time.sleep(0.5)

    def receiver_thread(self, address, message: str):
        # This is a function used as a thread for receiving
        split_msg = message.strip().split(',')

        if split_msg[0] == 'CMD' and int(split_msg[1]) == hardcoded.TEAM_ID:

            cmd_echo = (split_msg[2] + split_msg[3]) if len(split_msg) > 3 else split_msg[2]

            self.__data_maintained.write_value(MaintainedKeys.CMD_ECHO, cmd_echo)
            if split_msg[2] == 'CX':  # Enable and disable telemetry CMD,<TEAM_ID>,CX,<ON_OFF>
                if split_msg[3] == 'ON':
                    self.__data_maintained.write_value(MaintainedKeys.CX_TX, True)

                    self.__logger.info("CMD: CX ON")
                    print("CMD: CX ON")

                elif split_msg[3] == 'OFF':
                    self.__data_maintained.write_value(MaintainedKeys.CX_TX, False)

                    self.__logger.info("CMD: CX OFF")
                    print("CMD: CX OFF")

            elif split_msg[2] == 'ST':  # Set time CMD,<TEAM_ID>,ST,<UTC_TIME>
                self.__update_time(self.__crap_time_to_unix(split_msg[3]))

                self.__logger.info("CMD: ST" + self.__get_time())
                print("CMD: ST", self.__get_time())

            elif split_msg[2] == 'SIM':  # Enable, disable and activate sim mode CMD,<TEAM_ID>,SIM,<MODE>
                mode = split_msg[3]
                if mode == 'DISABLE':
                    self.__sim_mode = False
                    self.__hardware.air_pressure.stop_override()

                    self.__logger.info("CMD: SIM DISABLE")
                    print("CMD: SIM DISABLE")

                elif mode == 'ENABLE':
                    self.__sim_mode = True

                    self.__logger.info("CMD: SIM ENABLE")
                    print("CMD: SIM ENABLE")

                elif mode == 'ACTIVATE' and self.__sim_mode:
                    self.__hardware.air_pressure.start_override()

                    self.__logger.info("CMD: SIM ACTIVATE")
                    print("CMD: SIM ACTIVATE")

            elif split_msg[2] == 'SIMP':  # Sim mode data point CMD,<TEAM ID>,SIMP,<PRESSURE>
                self.__hardware.air_pressure.input_sim_data(int(split_msg[3]))

            elif split_msg[2] == 'RST':  # Reset cansat states CMD,<TEAM ID>,RST
                self.__data_maintained.reset()

                self.__logger.info("CMD: RESET")
                print("CMD: RESET")

            elif split_msg[2] == 'HEALTH':  # Returns health message CMD,<TEAM ID>,HEALTH
                self.__health_message()

                self.__logger.info("CMD: SIM HEALTH")
                print("CMD: SIM HEALTH")

            else:
                self.__logger.warning("Received invalid command: {}".format(message))

        else:
            try:
                if split_msg[0] == str(hardcoded.TEAM_ID) and split_msg[3] == 'X':
                    if split_msg[4] == 'TR':
                        packet = [  # Payload Telemetry Packet
                            hardcoded.TEAM_ID,  # Team ID
                            self.__get_mission_time(),  # Mission Time
                            -1,  # Packet Count
                            'T',  # Packet Type
                            split_msg[5],  # TP_Alt
                            split_msg[6],  # TP_Temp
                            split_msg[7],  # TP_Voltage
                            split_msg[8],  # Gyro_R
                            split_msg[9],  # Gyro_P
                            split_msg[10],  # Gyro_Y
                            split_msg[11],  # Accel_R
                            split_msg[12],  # Accel_P
                            split_msg[13],  # Accel_Y
                            split_msg[14],  # Mag_R
                            split_msg[15],  # Mag_P
                            split_msg[16],  # Mag_Y
                            split_msg[17],  # Pointing Error
                            split_msg[18],  # TP_Software_State
                        ]

                        self.__data_maintained.write_value(MaintainedKeys.PAYLOAD_STATE, split_msg[18])
                        self.__transmit(packet, XBeeAddress.GROUND)

                    elif split_msg[4] == 'SU':
                        if split_msg[5] == 'LAUNCH_STANDBY':
                            state = PayloadStates.LAUNCH_STANDBY
                        elif split_msg[5] == 'STANDBY':
                            state = PayloadStates.STANDBY
                        elif split_msg[5] == 'RELEASED':
                            state = PayloadStates.RELEASED
                        elif split_msg[5] == 'STABILISE':
                            state = PayloadStates.STABILISE
                        elif split_msg[5] == 'LANDED':
                            state = PayloadStates.LANDED

                        self.__data_maintained.write_value(MaintainedKeys.PAYLOAD_STATE, state)

                        self.__logger.info("CMD: STATE PAY: ".format(state))
                        print("CMD: STATE PAY: ", split_msg[5], state)

                    else:
                        self.__logger.warning("Received invalid message: {}".format(message))

                else:
                    self.__logger.warning("Received invalid message: {}".format(message))
            except:
                self.__logger.warning("Received invalid message: {}".format(message))

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

    def __container_telemetry(self):
        # This is a function used as a thread for transmitting container telemetry to ground xbee
        while self.__running:
            if self.__data_maintained.read_value(MaintainedKeys.CX_TX):
                container_state = self.__data_maintained.read_value(MaintainedKeys.CONTAINER_STATE)

                if container_state == ContainerStates.LAUNCH_WAIT:
                    state = 'LAUNCH_WAIT'
                elif container_state == ContainerStates.ASCENT:
                    state = 'ASCENT'
                elif container_state == ContainerStates.ROCKET_SEPARATION:
                    state = 'ROCKET_SEPARATION'
                elif container_state == ContainerStates.DESCENT:
                    state = 'DESCENT'
                elif container_state == ContainerStates.TP_RELEASE:
                    state = 'TP_RELEASE'
                elif container_state == ContainerStates.LANDED:
                    state = 'LANDED'

                gps_data = self.__hardware.gps.get_data()

                packet = [  # Container Packet
                    hardcoded.TEAM_ID,  # Team ID
                    self.__get_mission_time(),  # Mission Time
                    -1,  # Packet Count
                    'C',  # Packet Type
                    'S' if self.__sim_mode else 'F',  # Simulation Mode
                    'R' if container_state >= ContainerStates.TP_RELEASE else 'N',  # Payload Release
                    'R' if container_state >= ContainerStates.DESCENT else 'N',  # Parachute Release
                    "{:.1f}".format(self.get_height()),  # Altitude
                    "{:.1f}".format(self.__hardware.temperature.get_data()),  # Temp
                    "{:.2f}".format(self.__hardware.voltage.get_data()),  # Voltage
                    gps_data[0],  # GPS time
                    gps_data[1],  # GPS lat
                    gps_data[2],  # GPS long
                    gps_data[3],  # GPS alt
                    gps_data[4],  # GPS status
                    state,  # Container State
                    self.__data_maintained.read_value(MaintainedKeys.CMD_ECHO)  # CMD_Echo
                ]

                self.__transmit(packet, XBeeAddress.GROUND)

            time.sleep(1)

    def __boot_message(self):
        packet = [  # Boot Packet
            hardcoded.TEAM_ID,  # Team ID
            self.__get_mission_time(),  # Mission Time
            -1,  # Packet Count
            'X',  # Packet Type
            'BC',  # Other Packet Type: Boot Container
        ]

        self.__transmit(packet, XBeeAddress.GROUND, False)

    def __health_message(self):
        packet = [  # Boot Packet
            hardcoded.TEAM_ID,  # Team ID
            self.__get_mission_time(),  # Mission Time
            -1,  # Packet Count
            'X',  # Packet Type
            'HCC',  # Other Packet Type: Health Check Container
            "{:.2f}".format(self.__hardware.pi.get_temp()),
            "{:.2f}".format(self.__hardware.pi.get_load()),
            "{:.2f}".format(self.__hardware.pi.get_disk())
        ]

        self.__transmit(packet, XBeeAddress.GROUND, False)

    def __payload_telemetry_request(self):
        while self.__data_maintained.read_value(MaintainedKeys.CONTAINER_STATE) == ContainerStates.TP_RELEASE:
            if self.__data_maintained.read_value(MaintainedKeys.CX_TX):
                packet = [  # Payload Request Packet
                    hardcoded.TEAM_ID,  # Team ID
                    self.__get_mission_time(),  # Mission Time
                    -1,  # Packet Count
                    'X',  # Packet Type
                    'TS',  # Other Packet Type: Telemetry Solicitation
                ]

                self.__transmit(packet, XBeeAddress.PAYLOAD, False)
            time.sleep(0.25)

    def __payload_state_update(self):
        container_state = self.__data_maintained.read_value(MaintainedKeys.CONTAINER_STATE)

        if container_state == ContainerStates.LAUNCH_WAIT:
            state = 'LAUNCH_WAIT'
        elif container_state == ContainerStates.ASCENT:
            state = 'ASCENT'
        elif container_state == ContainerStates.ROCKET_SEPARATION:
            state = 'ROCKET_SEPARATION'
        elif container_state == ContainerStates.DESCENT:
            state = 'DESCENT'
        elif container_state == ContainerStates.TP_RELEASE:
            state = 'TP_RELEASE'
        elif container_state == ContainerStates.LANDED:
            state = 'LANDED'

        packet = [  # Payload State Update Packet
            hardcoded.TEAM_ID,  # Team ID
            self.__get_mission_time(),  # Mission Time
            -1,  # Packet Count
            'X',  # Packet Type
            'SU',  # Other Packet Type: State Update
            state
        ]

        self.__transmit(packet, XBeeAddress.PAYLOAD, False)
        print("PSU: ", state)

    def __payload_reset(self):
        packet = [  # Payload State Update Packet
            hardcoded.TEAM_ID,  # Team ID
            self.__get_mission_time(),  # Mission Time
            -1,  # Packet Count
            'X',  # Packet Type
            'RST'  # Other Packet Type: RESET
        ]

        self.__transmit(packet, XBeeAddress.PAYLOAD, False)
        print("PRST: ", packet)

    def __camera_update(self):
        # This is a function called by the camera listener on state updates
        state = self.__data_maintained.read_value(MaintainedKeys.CONTAINER_STATE)

        if self.__hardware.camera is not None:
            if ContainerStates.ASCENT <= state < ContainerStates.LANDED:
                if not self.__hardware.camera.is_activated():
                    self.__hardware.camera.activate()
            else:
                self.__hardware.camera.deactivate()

    def __parachute_update(self):
        # This is a function called by the parachute release listener on state updates
        state = self.__data_maintained.read_value(MaintainedKeys.CONTAINER_STATE)

        if state >= ContainerStates.DESCENT:
            self.__hardware.parachute.activate()

    def __payload_update(self):
        # This is a function called by the parachute release listener on state updates
        state = self.__data_maintained.read_value(MaintainedKeys.CONTAINER_STATE)

        if state >= ContainerStates.TP_RELEASE:
            self.__hardware.payload.activate()

    def __beacon_update(self):
        # This is a function called by the beacon listener on state updates
        state = self.__data_maintained.read_value(MaintainedKeys.CONTAINER_STATE)

        if state >= ContainerStates.LANDED:
            self.__hardware.buzzer.activate()

    def __perform_reset(self):
        self.__logger.info("Performing RESET")

        self.__payload_reset()

        self.__data_maintained.reset()
        self.__data_backups.stop()
        self.__data_backups = Backup("container")

        self.__hardware.buzzer.disable()

        # Disable override
        self.__running = True
        self.__sim_mode = False
        self.__hardware.air_pressure.stop_override()
        self.__landed_timer = 0

        self.__boot_message()

    def get_height(self, offset=True):
        # This function is used to poll the pressure and temperature sensor to get altitude
        pressure = self.__hardware.air_pressure.get_data() * 100  # in Pa
        temp = self.__hardware.temperature.get_data() + 273.15  # in Kelvin
        # temp = self.__hardware.air_pressure.get_temp() + 273.15 # Backup?

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


class ContainerHardware:
    def __init__(self, logger):
        self.__i2c = board.I2C()
        self.__bus = smbus.SMBus(1)

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
        self.gps = GPS(self.__bus)
        self.temperature = Temperature(self.__i2c)
        self.voltage = Voltage()

        self.gps.activate()

        # Camera
        try:
            self.camera = Camera()
        except:
            print("ERROR Unable to start Camera")
            logger.error("ERROR Unable to start Camera")
            self.camera = None

        # Mechanisms
        self.parachute = ParachuteRelease()
        self.payload = PayloadRelease()
        self.buzzer = BuzzerMech()
