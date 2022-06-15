import os
from CFS.payload import Payload

def is_root():
    return os.geteuid() == 0

if is_root():
    Payload()

else:
    print("Restart program with sudo")