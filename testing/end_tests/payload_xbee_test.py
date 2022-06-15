import logging

from CFS.Data import hardcoded
from CFS.Data.logger import setup_logging
from CFS.Listeners.xbeelistener import XbeeListener
from CFS.container import ContainerHardware
from CFS.enums import ContainerStates, XBeeAddress, MaintainedKeys
from CFS.payload import PayloadHardware


def output(address, message: str):
    split_msg = message.split(',')
    print(split_msg)


def transmit(packet, address):
    packet_count = 5
    packet[2] = packet_count

    output = ''
    for line in packet:
        output += str(line)
        output += ','

    output = output[:-1] + "\n"

    if payload.xbee is not None:
        payload.xbee.send(output, address)
        logger.info("XBEE Output: " + output)

    else:
        logger.info("XBEE Unavailable Error: " + output)


def payload_telemetry_request():
    packet = [  # Payload Request Packet
        hardcoded.TEAM_ID,  # Team ID
        0,  # Null
        -1,  # Packet Count
        'X',  # Packet Type
        'TR',  # Other Packet Type: Telemetry Response
        0,
        payload.air_pressure.get_temp(),
        payload.voltage.get_data(),
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        5
    ]

    transmit(packet, XBeeAddress.CONTAINER)


def boot_message():
    packet = [  # Boot Packet
        hardcoded.TEAM_ID,  # Team ID
        0,  # Mission Time
        -1,  # Packet Count
        'X',  # Packet Type
        'BP',  # Other Packet Type: Boot Payload
    ]

    transmit(packet, XBeeAddress.GROUND)


def health_message():
    packet = [  # Boot Packet
        hardcoded.TEAM_ID,  # Team ID
        0,  # Mission Time
        -1,  # Packet Count
        'X',  # Packet Type
        'HCP',  # Other Packet Type: Health Check Payload
        payload.pi.get_temp(),
        payload.pi.get_load(),
        payload.pi.get_disk()
    ]

    transmit(packet, XBeeAddress.GROUND)


setup_logging("payload_xbee_test")
logger = logging.getLogger("Payload")
logger.info("Started Payload Logger")

payload = PayloadHardware(logger)

payload.xbee.add_listener(
    XbeeListener(output)
)

boot_message()
health_message()
payload_telemetry_request()

while True:
    msg = input()
    print("Transmit: ", msg)
    transmit([msg, 0, 0], XBeeAddress.GROUND)

