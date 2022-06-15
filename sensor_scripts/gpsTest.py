import smbus
import time

def calcChecksum(buf, bufLen):
    CK_A = 0
    CK_B = 0

    # print('\nbuf: ~~~')
    # print(list(map(hex, buf)))
    # print('\n')

    for i in range(bufLen):
        CK_A = (CK_A + buf[2 + i]) % 256
        CK_B = (CK_B + CK_A) % 256

    return CK_A, CK_B


def writeMsg(msg):

    msg[-2], msg[-1] = calcChecksum(msg, len(msg) - 4)

    print('msg: ')
    print(list(map(ascii, msg)))
    print('\n')

    bus.write_i2c_block_data(device, 0xff, msg)


bus = smbus.SMBus(1)
time.sleep(1)

device = 0x48
maxLen = 32
len_reg = 0xFD

while True:

    # -- reading available data count
    # 1) read single bytes from len registers
    len1 = bus.read_byte_data(device, len_reg)
    len2 = bus.read_byte_data(device, len_reg + 1)
    total = len1 * 256 + len2
    print("Total Bytes: %i" % (total))

    # poll MON-VER - firmware version
    writeMsg([
        0xb5, 0x62,  # header
        0x0a, 0x04,  # msg id
        0x00, 0x00,  # length
        0xff, 0xff,  # checksum
    ])
    
    time.sleep(1)
    
    # -- reading available data count
    # 1) read single bytes from len registers
    len1 = bus.read_byte_data(device, len_reg)
    len2 = bus.read_byte_data(device, len_reg + 1)
    #print("%02x %02x" % (len1, len2))
    total = len1 * 256 + len2
    print("Total Bytes: %i" % (total))
    
    # 2) read block from 0x00
    #data2 = bus.read_i2c_block_data(device, 0x00, 32)
    data = []
    for i in range(total):
        data.append(bus.read_byte_data(device, 0xff))
    print('MON-VER (Receiver/Software Version): ')
    print('Header: [{}]'.format(', '.join(hex(x) for x in data[:2])))
    print('ID: [{}]'.format(', '.join(hex(x) for x in data[2:4])))
    print('Length: ', data[4] + (data[5] << 2))
    print('Payload:\n==========')
    print(bytes(data[6:36]).decode('utf8'))
    print(bytes(data[36:46]).decode('utf8'))
    print(bytes(data[46:76]).decode('utf8'))
    print(bytes(data[76:106]).decode('utf8'))
    print('==========')
    print('Checksum (CK_A CK_B): [{}]'.format(', '.join(hex(x) for x in data[2:4])))
    
    # print('\n')
    # print(list(map(ascii, data)))
    
    print('\n')

    time.sleep(20)
