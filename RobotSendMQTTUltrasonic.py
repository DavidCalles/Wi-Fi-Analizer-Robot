# importing sys
import sys
# importing picar-x classes to the system path
sys.path.append('RobotSource/picar-x/')
import picarx as pix
# importing own classes for ultrasonic sensor calibration
sys.path.append('UltrasonicSensor/RpiUltrasonic/')
import RpiUltrasonic as rpius
# importing own functions for mqtt connetion
sys.path.append('Network_Connections/MQTT_Connection/')
import MQTT_Publisher as mymqtt
##
import time 
import os  
from datetime import datetime 
 
##=============================================================================
# Create robot object
myrobot = pix.Picarx()

# Calibrate system if it is the first time
calibPath = "UltrasonicSensor/RobotUltraSensor/UltrasonicSensorCalibration.npz"
# Calibration object
myCalib = rpius.UltrasonicSensor(trigger_pin=27, echo_pin=22)

# Calibrate sensor in case it wasnt calibrated
if os.path.exists(calibPath) and os.path.getsize(calibPath) > 0:
    # Non empty file exists
    myCalib.ImportCalibrationFromFile(calibPath)
else:
    myCalib.CalibrateSemiAutomatic(1)
    myCalib.ExportCalibrationToFile(calibPath)

# Set new connection for sending data   
connection0 = mymqtt.NewMQTTPublisher("raspi0")
connection0.publish("Start Data")
connection0.publish("SampleId, DateTime(UTC), RawDistance(cm), CalibratedDistance(cm)")
sampleId=0
while (1):
    time.sleep(3)
    # Get  ultrasonic sensor data
    distanceRaw = myrobot.get_distance()
    distanceCalib = rpius.CalibrateSample(distanceRaw, myCalib.coeffs)
    connection0.publish(f"{sampleId}, {datetime.now()}, {distanceRaw:.2f}, {distanceCalib:.2f}")
    sampleId+=1
    
connection0.publish("End Data")
connection0.disconnect()