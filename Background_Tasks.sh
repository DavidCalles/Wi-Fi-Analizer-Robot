#!/bin/bash

# Potentially need to run from the project directory
PROJECT_DIR=/home/davidcalles/Documents/Wi-Fi-Analizer-Robot/

# Run User-Input related code
python3 $(PROJECT_DIR)UserInput/TestOutputToFile.py > $(PROJECT_DIR)UserInput/OutputText.txt &

# Run LIDAR collecting system (better do it with systemd every second)
python3 $(PROJECT_DIR)SLAM/SLAM-on-Raspberry-Pi/rpslam-thread.py &

# Get Wifi Data (Better do it with systemd every second)
/bin/bash $(PROJECT_DIR)Retrieve_Wi-Fi_Data/getWiFiData.sh &

# Get Picture from camera Data (Better do it with systemd every second)
python3 $(PROJECT_DIR)CameraCalibration/TakePicture.py &

# Run Manual Navigation system
python3 $(PROJECT_DIR)/RobotTests.py &

