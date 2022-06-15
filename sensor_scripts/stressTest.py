import os
import subprocess
import logging
import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3004 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
from time import sleep
import sys
import RPi.GPIO as GPIO
import time

def main():

    logging.basicConfig(filename='stress.log', filemode='a', encoding='utf-8', level=logging.DEBUG)

    triggerPIN = 18
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(triggerPIN,GPIO.OUT)
    GPIO.setwarnings(False)

    buzzer = GPIO.PWM(triggerPIN, 2700) # Set frequency to 1 Khz

    # create the spi bus
    spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)

    # create the cs (chip select)
    cs = digitalio.DigitalInOut(board.D5)

    # create the mcp object
    mcp = MCP.MCP3004(spi, cs, ref_voltage=3.3*2.6)

    logging.info('Starting Stress Test at ' + time.asctime())
    #logging.warning('And this, too')

    buzzer.start(50) # Set dutycycle to 10
    sleep(1)
    buzzer.stop()
    sleep(1)

    stressing = subprocess.Popen(['stress','-c','6'], stdout = subprocess.PIPE)

    output = stressing.stdout.readline().strip().decode('utf-8')
    print(output)
    logging.debug(output)

    # create an analog input channel on pin 0
    chan = AnalogIn(mcp, MCP.P0)
    while chan.voltage > 6.2: #setting 3.1V minimum
        sleep(60)
        print('ADC Voltage: ' + str(chan.voltage) + 'V')
        logging.debug('ADC Voltage: ' + str(chan.voltage) + 'V')

        stream = os.popen('vcgencmd measure_temp')
        output = stream.read().strip()
        print(output)
        logging.debug(output)



    buzzer.start(50) # Set dutycycle to 10
    sleep(0.5)
    buzzer.stop()
    sleep(0.5)
    buzzer.start(50) # Set dutycycle to 10
    sleep(0.5)
    buzzer.stop()

    logging.info('Stopping Stress Test at ' + time.asctime())
    stressing.kill()
    os.system('killall stress')
    logging.info('Stress Halted')
    
    GPIO.cleanup()
    sys.exit()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nInterrupted')
        os.system('killall stress')
        logging.warning('Stopped Manually at ' + time.asctime())
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
