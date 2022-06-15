import re

regexp_sent = re.compile("digi\.xbee\.sender - DEBUG - XBeeSerialPort '/dev/ttyS0' - SENT -")

f = open("output.txt", "w")

with open("payload-2022_06_03-07_25_34_AM.log") as file:
    for line in file:
        if re.search("digi\.xbee\.sender - DEBUG - XBeeSerialPort '/dev/ttyS0' - SENT -", line):
            f.write(line.split(":")[3] + "\n")


