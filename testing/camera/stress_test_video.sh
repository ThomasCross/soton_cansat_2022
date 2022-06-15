#!/bin/bash
# Script to stress test pi, while performing video/camera tasks

function temps {
    gpu=$(/opt/vc/bin/vcgencmd measure_temp)
    cpu=$(</sys/class/thermal/thermal_zone0/temp)
    load=$(uptime)

    echo -e "CPU  => $((cpu/1000)) c\nGPU  => $gpu\nLOAD => $load"
}

echo "$(date) @ $(hostname)"
echo "-------------------------------------------"
echo "Start Values"
temps


# Test loop

sudo raspivid -o /var/www/html/testing/video/stress.h264 -w 1280 -h 720 -fps 30 -t 600000 -ex sports& >/dev/null
for i in {1..60}
do
    stress -c 3 -i 1 -m 1 --vm-bytes 128M -t 10s >/dev/null
    #sleep 10
    echo "-------------------------------------------"
    echo "$(date) ~ $i"
    temps
done
