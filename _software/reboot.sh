#!/bin/bash

echo "Killing Python..."
sudo killall python
echo "Starting Back Up..."
sudo python /home/pi/Documents/DataLogger/_software/main.py
#exit(0)