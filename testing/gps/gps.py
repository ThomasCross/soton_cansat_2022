import time
import json
import smbus
import logging

address = 0x42
gpsReadInterval = 0.1

# GUIDE
# http://ava.upuaut.net/?p=768

GPSDAT = {
    'strType': None,
    'fixTime': None,
    'lat': None,
    'latDir': None,
    'lon': None,
    'lonDir': None,
    'fixQual': None,
    'numSat': None,
    'horDil': None,
    'alt': None,
    'altUnit': None,
    'galt': None,
    'galtUnit': None,
    'DPGS_updt': None,
    'DPGS_ID': None
}


def parseResponse(gpsLine):
    print(gpsLine)

    gpsChars = ''.join(chr(c) for c in gpsLine)

    print(gpsChars)
    if "*" not in gpsChars:
        return False

    gpsStr, chkSum = gpsChars.split('*')
    gpsComponents = gpsStr.split(',')
    gpsStart = gpsComponents[0]
    if gpsStart == "$GNGGA":
        chkVal = 0
        for ch in gpsStr[1:]:  # Remove the $
            chkVal ^= ord(ch)
        if chkVal == int(chkSum, 16):
            for i, k in enumerate(
                    ['strType', 'fixTime',
                     'lat', 'latDir', 'lon', 'lonDir',
                     'fixQual', 'numSat', 'horDil',
                     'alt', 'altUnit', 'galt', 'galtUnit',
                     'DPGS_updt', 'DPGS_ID']):
                GPSDAT[k] = gpsComponents[i]
            print("2: ", gpsChars)
            print("3: ", json.dumps(GPSDAT, indent=2))


def readGPS(busi2c):
    c = None
    response = []
    # try:
    while True:  # Newline, or bad char.
        c = busi2c.read_byte(address)
        if c == 255:
            return False
        elif c == 10:
            break
        else:
            response.append(c)
    parseResponse(response)


# except Exception as e:
#    print("Error 1: ", e)


bus = smbus.SMBus(1)
counter = 0

while True:
    print("Attempt: ", counter)
    counter += 1
    readGPS(bus)
    time.sleep(gpsReadInterval)
