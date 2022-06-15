# This file is used to store and return hard coded data

# Team Information
TEAM_ID = 1032

# Default File Locations
MAINTAINED_FILE = "/cansat/maintained.txt"
BACKUPS_PATH = "/cansat/backups/"

# Communication XBee MAC Addresses
XBEE_CONTAINER = "0013A20041CF05CC"
XBEE_PAYLOAD = "0013A20041CF05EB"
XBEE_GROUND = "0013A20041CCAB73"  # <-- SMA connector or "0013A20041CF05D7"

# Mechanism Pins and Data
CON_PIN_PARACHUTE_SERVO = 26        # Container Parachute Release Constants
CON_INIT_PARACHUTE_SERVO = -0.75
CON_ACTI_PARACHUTE_SERVO = 1

PAY_PIN_PAYLOAD_SERVO = 25           # Payload Release Constants
PAY_INIT_PAYLOAD_SERVO = -1
PAY_ACTI_PAYLOAD_SERVO = 1

PAY_PIN_STABILISATION_IN1 = 17      # Payload Stabilisation Constants
PAY_PIN_STABILISATION_IN2 = 18
PAY_PIN_STABILISATION_IN3 = 27
PAY_PIN_STABILISATION_IN4 = 26

BOT_PIN_Buzzer = 18                 # Buzzer Constants

# Camera Settings and File Path
CAMERA_PATH = "/cansat/camera/"

RESOLUTION = (1280, 720)
FRAMERATE = 30
SEG_LENGTH = 10
