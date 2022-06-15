import logging

from CFS.Data import hardcoded
from CFS.enums import XBeeAddress
from CFS.Listeners.xbeelistener import XbeeListener
from digi.xbee.devices import XBeeDevice, RemoteXBeeDevice
from digi.xbee.models.address import XBee64BitAddress


class Xbee:
    # This class is used to send and receive data via the XBee

    def __init__(self):
        # Start logger
        self.__logger = logging.getLogger("XBee")
        self.__logger.info("Started XBee Logger")

        # Init XBee
        self.__xbee = XBeeDevice("/dev/ttyS0", 9600)
        self.__xbee.open()

        # Init Remote XBees
        self.__container = RemoteXBeeDevice(self.__xbee, XBee64BitAddress.from_hex_string(hardcoded.XBEE_CONTAINER))
        self.__payload = RemoteXBeeDevice(self.__xbee, XBee64BitAddress.from_hex_string(hardcoded.XBEE_PAYLOAD))
        self.__ground = RemoteXBeeDevice(self.__xbee, XBee64BitAddress.from_hex_string(hardcoded.XBEE_GROUND))

        # Add receiving
        self.__xbee.add_data_received_callback(self.__receive_data)
        self.__listeners = []

    def add_listener(self, listener: XbeeListener):
        # Add receiving listener
        self.__listeners.append(listener)

    def remove_listener(self, listener: XbeeListener):
        # Remove receiving listener
        self.__listeners.remove(listener)

    def notify(self, address, message):
        # Notify receiving listener
        for listener in self.__listeners:
            listener.notify(address, message)

    def __receive_data(self, xbee_message):
        # Receives xbee messages and forwards to notifier
        address = xbee_message.remote_device.get_64bit_addr()
        data = xbee_message.data.decode("utf8")

        self.__logger.info("Message From({}): ".format(address, data))

        self.notify(address, data)

    def send(self, message, remote: XBeeAddress):
        # Send message via XBee to remote XBee
        for i in range(1, 3):  # Retry 3 times
            try:
                address = XBee64BitAddress.from_hex_string(remote)

                if address == self.__container.get_64bit_addr():
                    self.__xbee.send_data(self.__container, message)

                elif address == self.__payload.get_64bit_addr():
                    self.__xbee.send_data(self.__payload, message)

                elif address == self.__ground.get_64bit_addr():
                    self.__xbee.send_data(self.__ground, message)

                else:
                    self.__logger.error(
                        "XBee failed to send message ({}) to ({}) doesn't exist".format(
                            message,
                            remote
                        )
                    )
                    break

            except Exception as e:  # Log and Retry
                self.__logger.error(
                    "XBee failed to send message ({}) to ({}) Attempt {}: {}".format(
                        message,
                        remote,
                        i,  # Retry No.
                        e  # Exception Message
                    )
                )
                if i >= 3:  # Failed too many times
                    self.__logger.error("Failed to send message")

            else:  # Success break loop and continue
                break

    def close(self):
        # This closes the connection to the xbee
        self.__xbee.close()
