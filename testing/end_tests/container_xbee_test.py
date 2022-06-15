from datetime import datetime
import logging
import time

from CFS.Data import hardcoded
from CFS.Data.logger import setup_logging
from CFS.Listeners.xbeelistener import XbeeListener
from CFS.container import ContainerHardware
from CFS.enums import ContainerStates, XBeeAddress


def output(address, message: str):
    # This is a function used as a thread for receiving
    split_msg = message.strip().split(',')
    print(split_msg)

    if split_msg[0] == 'CMD' and int(split_msg[1]) == hardcoded.TEAM_ID:

        cmd_echo = (split_msg[2] + split_msg[3]) if len(split_msg) > 3 else split_msg[2]

        if split_msg[2] == 'CX':  # Enable and disable telemetry CMD,<TEAM_ID>,CX,<ON_OFF>
            if split_msg[3] == 'ON':
                print("Telm On")
            elif split_msg[3] == 'OFF':
                print("Telm Off")

        elif split_msg[2] == 'ST':  # Set time CMD,<TEAM_ID>,ST,<UTC_TIME>
            update_time(crap_time_to_unix(split_msg[3]))
            print("Time: ", get_time())

        elif split_msg[2] == 'SIM':  # Enable, disable and activate sim mode CMD,<TEAM_ID>,SIM,<MODE>
            mode = split_msg[3]
            if mode == 'DISABLE':
                print("Sim Disable")

            elif mode == 'ENABLE':
                print("Sim Enable")

            elif mode == 'ACTIVATE':
                print("Sim Activate")

        elif split_msg[2] == 'SIMP':  # Sim mode data point CMD,<TEAM ID>,SIMP,<PRESSURE>
            print("Sim Val: ", split_msg[3])

        elif split_msg[2] == 'RST':  # Reset cansat states CMD,<TEAM ID>,RST
            print("Reset")

        elif split_msg[2] == 'HEALTH':  # Returns health message CMD,<TEAM ID>,HEALTH
            print("Health")
            health_message()

        elif split_msg[2] == 'TESTSTATE':
            print("State: ", split_msg[3])
        else:
            print("Received invalid command: {}".format(message))

    else:
        try:
            if not (split_msg[3] == 'X' and (split_msg[4] == 'TR' or split_msg[4] == 'SU')):
                print("Received invalid message: {}".format(message))
            else:
                print("Received X message: {}".format(message))
        except:
            print("Received invalid message: {}".format(message))


def crap_time_to_unix(time):
    base = 1654383600

    split_time = time.split(":")

    return base + (3600 * int(split_time[0])) + (60 * int(split_time[1])) + int(split_time[2])


def update_time(unix):
    clk_id = time.CLOCK_REALTIME
    time.clock_settime(clk_id, float(unix))


def get_time():
    return datetime.fromtimestamp(time.time()).strftime('%H:%M:%S')


def transmit(packet, address):
    packet_count = 5
    packet[2] = packet_count

    output = ''
    for line in packet:
        output += str(line)
        output += ','

    output = output[:-1] + "\n"

    if container.xbee is not None:
        container.xbee.send(output, address)
        logger.info("XBEE Output: " + output)

    else:
        logger.info("XBEE Unavailable Error: " + output)


def container_telemetry():
    # This is a function used as a thread for transmitting container telemetry to ground xbee
    container_state = ContainerStates.DESCENT

    gps_data = container.gps.get_data()

    packet = [  # Container Packet
        hardcoded.TEAM_ID,  # Team ID
        get_time(),  # Mission Time
        -1,  # Packet Count
        'C',  # Packet Type
        'S' if False else 'F',  # Simulation Mode
        'R' if container_state >= ContainerStates.TP_RELEASE else 'N',  # Payload Release
        'R' if container_state >= ContainerStates.DESCENT else 'N',  # Parachute Release
        0,  # Altitude
        container.temperature.get_data(),  # Temp
        container.voltage.get_data(),  # Voltage
        gps_data[0],  # GPS time
        gps_data[1],  # GPS lat
        gps_data[2],  # GPS long
        gps_data[3],  # GPS alt
        gps_data[4],  # GPS status
        container_state,  # Container State TODO: State to string function
        'CMD ECHO'  # CMD_Echo
    ]

    transmit(packet, XBeeAddress.GROUND)


def boot_message():
    packet = [  # Boot Packet
        hardcoded.TEAM_ID,  # Team ID
        get_time(),  # Mission Time
        -1,  # Packet Count
        'X',  # Packet Type
        'BC',  # Other Packet Type: Boot Container
    ]

    transmit(packet, XBeeAddress.GROUND)


def health_message():
    packet = [  # Boot Packet
        hardcoded.TEAM_ID,  # Team ID
        get_time(),  # Mission Time
        -1,  # Packet Count
        'X',  # Packet Type
        'HCC',  # Other Packet Type: Health Check Container
        container.pi.get_temp(),
        container.pi.get_load(),
        container.pi.get_disk()
    ]

    transmit(packet, XBeeAddress.GROUND)


setup_logging("container_xbee_test")
logger = logging.getLogger("Container")
logger.info("Started Container Logger")

container = ContainerHardware(logger)

container.xbee.add_listener(
    XbeeListener(output)
)

boot_message()
health_message()
container_telemetry()

while True:
    msg = input()

    if msg == "time":
        print(get_time())
        container_telemetry()
    else:
        print("Transmit: ", msg)
        transmit([msg, 0, 0], XBeeAddress.GROUND)
