import re

f = open("output2.txt", "w")

with open("cyber") as file:
    for line in file:
        data = line.split(",")

        miss_time = data[1].split(":")

        miss_time[0] = '18'
        miss_time[1] = '07'

        temp = str(int(miss_time[2]) - 5)

        if len(temp) == 1:
            temp = '0' + temp
        miss_time[2] = temp

        packet = [  # Payload Telemetry Packet
            1032,  # Team ID
            ':'.join(miss_time),  # Mission Time
            data[2],  # Packet Count
            'T',  # Packet Type
            data[5],  # TP_Alt
            data[6],  # TP_Temp
            data[7],  # TP_Voltage
            data[8],  # Gyro_R
            data[9],  # Gyro_P
            data[10],  # Gyro_Y
            data[11],  # Accel_R
            data[12],  # Accel_P
            data[13],  # Accel_Y
            data[14],  # Mag_R
            data[15],  # Mag_P
            data[16],  # Mag_Y
            data[17],  # Pointing Error
            data[18],  # TP_Software_State
        ]

        output1 = ''
        for point in packet:
            output1 += str(point)
            output1 += ','

        output1 = output1[:-1]

        f.write(output1)
