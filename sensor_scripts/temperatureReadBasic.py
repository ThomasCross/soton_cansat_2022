import time
import board
import adafruit_tmp117

i2c = board.I2C()  # uses board.SCL and board.SDA
tmp117 = adafruit_tmp117.TMP117(i2c)

while True:
    print("Temperature: %.2f degrees C"%tmp117.temperature)
    time.sleep(0.5)
