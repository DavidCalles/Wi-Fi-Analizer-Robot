# importing sys
import sys
# importing picar-x classes to the system path
sys.path.append('RobotSource/picar-x/')
import picarx as pix
# importing own classes for ultrasonic sensor calibration
sys.path.append('UltrasonicSensor/RpiUltrasonic/')
import RpiUltrasonic as rpius
##
import time 
import os    
 
##=============================================================================
# Create robot object
myrobot = pix.Picarx()

# Calibrate system if it is the first time
calibPath = "UltrasonicSensor/RobotUltraSensor/UltrasonicSensorCalibration.npz"
# Calibration object
myCalib = rpius.UltrasonicSensor(trigger_pin=27, echo_pin=22)

# Calibrate sensor
if os.path.exists(calibPath) and os.path.getsize(calibPath) > 0:
    # Non empty file exists
    myCalib.ImportCalibrationFromFile(calibPath)
else:
    myCalib.CalibrateSemiAutomatic(1)
    myCalib.ExportCalibrationToFile(calibPath)

for i in range(10):
    # Get  ultrasonic sensor data
    distanceRaw = myrobot.get_distance()
    distanceCalib = rpius.CalibrateSample(distanceRaw, myCalib.coeffs)
    print(f'{distanceRaw}, {distanceCalib}')
    time.sleep(0.5)
    