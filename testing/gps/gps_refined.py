import time
import pynmea2
import smbus


def parseResponse(gpsLine):
    gpsChars = ''.join(chr(c) for c in gpsLine)
    if "*" not in gpsChars:
        return False

    try:
        msg = pynmea2.parse(gpsChars)

        try:
            timestamp = msg.timestamp
        except:
            timestamp = ''

        try:
            lat = msg.latitude
        except:
            lat = 0

        try:
            long = msg.longitude
        except:
            long = 0

        try:
            sat = msg.num_sats
        except:
            sat = 0
        try:
            alt = msg.altitude
            altunit = msg.altitude_units
        except:
            alt = 0
            altunit = 'N/A'

        print("Timestamp: ", timestamp, " LAT: ", lat, " LONG: ", long, " | ", sat, " ", alt, altunit)
    except pynmea2.ParseError as e:
        # print('Parse error: {}'.format(e))
        pass


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


address = 0x42
gpsReadInterval = 1
bus = smbus.SMBus(1)

while True:
    readGPS(bus)
    time.sleep(gpsReadInterval)
