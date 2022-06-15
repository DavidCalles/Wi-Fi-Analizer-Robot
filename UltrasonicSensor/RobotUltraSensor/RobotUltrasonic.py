# importing sys
import sys
# importing picar-x classes to the system path
sys.path.insert(0, '../../RobotSource/picar-x/')
import picarx as pix
# importing own classes for ultrasonic
sys.path.insert(0, '../ExternalUltrasensor/')
import RpiUltrasonic as rpius
##
import time 
import os   
 
##=============================================================================
# Create robot object
myrobot = pix.Picarx()

# Calibrate system if it is the first time
calibPath = "UltrasonicSensorCalibration.npz"
# Calibration object
myCalib = rpius.UltrasonicSensor()

# Calibrate sensor
if os.path.exists(calibPath) and os.path.getsize(calibPath) > 0:
    # Non empty file exists
    myCalib.ImportCalibrationFromFile(calibPath)
else:
    myCalib.CalibrateSemiAutomatic(2)
    myCalib.ExportCalibrationToFile(calibPath)

for i in range(20):
    # Get  ultrasonic sensor data
    distanceRaw = myrobot.get_distance()
    distanceCalib = rpius.CalibrateSample()