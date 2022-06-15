from collections.abc import Callable


class Listener:
    # This class is used to create listeners

    def __init__(self, subject: Callable):
        self.__subject = subject

    def notify(self):
        self.__subject()
