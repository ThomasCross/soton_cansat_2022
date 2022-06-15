# Python Code to communicate with MCP3004 by Fraser May

#Import SpiDev wrapper to enable hardware SPI
import spidev

#Establish SPI connection with Bus 0, Device 0
spi = spidev.SpiDev()
spi.open(0,0)

def get_adc(channel):
    #Check valid channel
    if((channel > 3) or (channel < 0)):
        return -1

    #Perform SPI transaction and store returned bits in 'r'
    r = spi.xfer([1, (8+channel)<<4, 0])
    #Filter data bits from returned bits
    adcout = ((r[1]&3) << 8) + r[2]
    #Return value from 0-1023
    return adcout


while True:
    print(get_adc(0))
