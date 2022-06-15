Command to sys link python
```
  sudo ln -s /home/soton/soton_cansat/CFS/ CFS
```

Bits to pip
- pyserial

Other bits
- sudo apt install python3-picamera

# Container

## States

| ID  | NAME              | Description                                       | State Change                                                    | Affected Elements                        |
|-----|-------------------|---------------------------------------------------|-----------------------------------------------------------------|------------------------------------------|
| 1   | LAUNCH_WAIT       | Preparing for launch / waiting on launch pad      | State Reset                                                     |                                          |
| 2   | ASCENT            | Going up in rocket till ejection/starting to fall | CANSAT 50m above start height                                   | Start Camera                             |
| 3   | ROCKET_SEPARATION | From ejection to main parachute deployment        | Ejection charge change in pressure / Altitude starts decreasing |                                          |
| 4   | DESCENT           | From main chute deployment to payload deployment  | CANSAT below 400m                                               | Main Parachute                           |
| 5   | TP_RELEASE        | Payload deployment to landed                      | CANSAT below 300m                                               | Release Payload, Start Payload Telemetry |
| 6   | LANDED            | Landed                                            | CANSAT below 50m for 30 seconds                                 | Start Beacon, Stop Camera and Telemetry  |

## Threads

| Name                | Boot Order | Purpose                         | Thread Requires               | Object Requires                                           |
|---------------------|------------|---------------------------------|-------------------------------|-----------------------------------------------------------|
| State               | 2          | Used to store and change states | Receiver                      | Altitude (Pressure/Temp)                                  |
| Parachute           | 6          | Deploy Parachute                | State                         | Parachute Mech                                            |
| Beacon              | 7          | Sound Beacon                    | State                         | Beacon Mech                                               |
| Camera              | 5          | Camera Operation                | State                         | Camera Object                                             |
| Receiver            | 1          | Receives Commands               | (NB, sends reset to Receiver) | XBee (NB, sends to RTC / system time and pressure sensor) |
| Container Telemetry | 3          | Sends Container Telemetry       | Receiver, State               | Sensors, Hard Data, Time Data, Maintained Data            |
| Payload Telemetry   | 4          | Sends Payload Telemetry         | Receiver, State               | WiFi, Hard Data, Time Data, Maintained Data               |



# Payload

## States

| ID  | NAME           | Description                                                  | State Change             | Affected Elements   |
|-----|----------------|--------------------------------------------------------------|--------------------------|---------------------|
| 1   | LAUNCH_STANDBY | Preparing for launch / waiting on launch pad                 | State Reset              |                     |
| 2   | STANDBY        | Awaiting Payload Deployment                                  | Container in ASCENT      | Start Camera        |
| 3   | RELEASED       | Payload being deployed (20 sec), payload container alt check | Container in TP_RELEASED | Start Deployment    |
| 4   | STABILISE      | Payload deployed, starting to stabilise                      | Wait 20 sec              | Start Stabilisation |
| 5   | LANDED         | Landed                                                       | Container in LANDED      | Stop Camera         |

## Threads

| Name          | Boot Order | Purpose                                           | Thread Requires | Object Requires                                |
|---------------|------------|---------------------------------------------------|-----------------|------------------------------------------------|
| State         | 2          | Used to store and change states                   | Receiver        |                                                |
| Receiver      | 1          | Used to get incoming poll and data from container |                 | WiFi_Client                                    |
| Stabilisation | 4          | Clue in the name                                  | State           | Rotation Sensor and Mechanism                  |
| Descent       | 5          | Deploy payload                                    | State           | Deploy                                         |
| Telemetry     | 3          | Respond to container polls for data               | Receiver        | Sensors, Hard Data, Time Data, Maintained Data |
| Camera        | 6          | Clue in the name                                  | State           | Camera                                         |

```
ssh-keygen -t ed25519

Enable camera I2c and SPI

sudo apt install python3-pip
sudo pip3 install --upgrade adafruit-python-shell
sudo pip3 install Adafruit-Blinka
sudo apt-get install python3-picamera
sudo apt install python3-smbus
sudo pip3 install adafruit-circuitpython-tmp117
sudo pip3 install adafruit-circuitpython-mcp3xxx
sudo pip3 install digi-xbee
sudo pip3 install pynmea2
sudo pip3 install adafruit-circuitpython-bno08x
sudo apt inatsll python-pigpio python3-pigpio

cd /usr/local/lib/python3.9/dist-packages/
sudo ln -s /home/soton/soton_cansat/CFS/ CFS

sudo mkdir /cansat
sudo chown soton:soton /cansat
mkdir /cansat/backups
mkdir /cansat/camera

timedatectl set-ntp 0
```
