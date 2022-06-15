from collections.abc import Callable


class XbeeListener:
    # This class is used to create xbee receiving listeners

    def __init__(self, subject: Callable):
        self.__subject = subject

    def notify(self, address, message):
        self.__subject(address, message)
