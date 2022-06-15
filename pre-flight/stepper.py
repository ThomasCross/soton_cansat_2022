import RPi.GPIO as GPIO
import time

in1 = 17
in2 = 18
in3 = 27
in4 = 26

step_count = 4096 # 5.625*(1/64) per step, 4096 steps is 360°

# defining stepper motor sequence (found in documentation http://www.4tronix.co.uk/arduino/Stepper-Motors.php)
step_sequence = [[1,0,0,1],
                 [1,0,0,0],
                 [1,1,0,0],
                 [0,1,0,0],
                 [0,1,1,0],
                 [0,0,1,0],
                 [0,0,1,1],
                 [0,0,0,1]] # magnet sequence. to move, fire the next/last output order in this sequence

motor_pins = [in1,in2,in3,in4]
motor_step_counter = 0

# setting up
GPIO.setmode( GPIO.BCM )
GPIO.setup( in1, GPIO.OUT )
GPIO.setup( in2, GPIO.OUT )
GPIO.setup( in3, GPIO.OUT )
GPIO.setup( in4, GPIO.OUT )

# initializing
GPIO.output( in1, GPIO.LOW )
GPIO.output( in2, GPIO.LOW )
GPIO.output( in3, GPIO.LOW )
GPIO.output( in4, GPIO.LOW )

while True:
    angle = int(input())

    if angle == 1000:
        break

    for i in range(int((abs(angle)/360)*4096)): # for each stepper step in the required angle
        for pin in range(4): # Write to each pin the required output of current step in magnet sequence
            GPIO.output( motor_pins[pin], step_sequence[motor_step_counter][pin]) # fire the next sequence of magnets
        if (angle>=0): # If positive (i.e. clockwise)
            motor_step_counter = (motor_step_counter - 1) % 8 # caps motor_step_counter to always be between 0-7 as it defines what the next magnet sequence to fire should be
        else:
            motor_step_counter = (motor_step_counter + 1) % 8 #
        time.sleep(0.0005)


# Clear up
GPIO.output( in1, GPIO.LOW )
GPIO.output( in2, GPIO.LOW )
GPIO.output( in3, GPIO.LOW )
GPIO.output( in4, GPIO.LOW )
