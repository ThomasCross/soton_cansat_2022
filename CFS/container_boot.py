import os

from CFS.container import Container


def is_root():
    return os.geteuid() == 0


if is_root():
    Container()

else:
    print("Restart program with sudo")