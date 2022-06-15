import smbus
import time

bus = smbus.SMBus(1)
time.sleep(1)

device = 0x11
maxLen = 32
len_reg = 0xFD


def calcChecksum(buf, bufLen):
    CK_A = 0
    CK_B = 0

    print('\nbuf: ~~~')
    print(list(map(hex, buf)))
    print('\n')

    for i in range(bufLen):
        CK_A = (CK_A + buf[2 + i]) % 256
        CK_B = (CK_B + CK_A) % 256

    return CK_A, CK_B


def writeMsg(msg):

    msg[-2], msg[-1] = calcChecksum(msg, len(msg) - 4)

    print('\nmsg: ')
    print(list(map(ascii, msg)))
    print('\n')

    bus.write_i2c_block_data(device, 0xff, msg)


while True:

    # -- poll or set configuration

    # CFG-PRT - Polls the configuration of the used I/O Port
    # writeMsg([
    #     0xb5, 0x62,  # header
    #     0x06, 0x00,  # msg id
    #     0x00, 0x00,  # length
    #     0xff, 0xff,  # checksum
    # ])

    # CFG-PRT - Port Configuration for DDC Port
    writeMsg([
        0xb5, 0x62,  # header
        0x06, 0x00,  # msg id
        0x14, 0x00,  # length
        0x00,  # port id for DDC
        0x00,  # reserved0
        0x00,  # tx ready pin configuration
        0x01,  # threshold: multiplied by 8 bytes
        0x23, 0x00, 0x00, 0x56,  # ddc mode flags
        0x00, 0x00, 0x00, 0x00,  # reserved3
        0x07, 0x00,  # mask which input protocols are active
        0x03, 0x00,  # mask which output protocols are active
        0x02, 0x00,  # flags
        0x00, 0x00,  # reserved5
        0xff, 0xff,  # checksum
    ])

    # poll MON-VER - firmware version
    writeMsg([
        0xb5, 0x62,  # header
        0x0a, 0x04,  # msg id
        0x00, 0x00,  # length
        0xff, 0xff,  # checksum
    ])

    # poll MON-HW - hardware status
    writeMsg([
        0xb5, 0x62,  # header
        0x0a, 0x09,  # msg id
        0x00, 0x00,  # length
        0xff, 0xff,  # checksum
    ])

    # -- reading available data count
    # 1) read single bytes from len registers
    len1 = bus.read_byte_data(device, len_reg)
    len2 = bus.read_byte_data(device, len_reg + 1)
    print("%02x %02x" % (len1, len2))

    if len1 < 0:
        len1 += 256
    if len2 < 0:
        len2 += 256

    total = len2 * 256 + len1
    print("total: %i" % (total))

    # 2) read word (two bytes?) from first len register
    len3 = bus.read_word_data(device, len_reg)
    print("%02x %02x" % (len3, 0))

    # -- reading data
    # 1) read block from 0xff
    data = bus.read_i2c_block_data(device, 0xff, maxLen)
    print('\ndata: ')
    print(list(map(ascii, data)))
    # 2) read block from 0x00
    data2 = bus.read_i2c_block_data(device, 0x00, maxLen)
    print('\ndata2: ')
    print(list(map(ascii, data2)))

    # 3) read bytes from 'device' (last used register?)
    data3 = []
    for i in range(maxLen):
        data3.append(bus.read_byte(device))
    print('\ndata3: ')
    print(list(map(ascii, data3)))

    # 4) read bytes from data stream register
    data4 = []
    for i in range(maxLen):
        data4.append(bus.read_byte_data(device, 0xff))
    print('\ndata4: ')
    print(list(map(ascii, data4)))

    print('\n')

    time.sleep(0.5)
