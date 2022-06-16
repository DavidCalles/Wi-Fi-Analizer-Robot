# importing sys
import sys
# # importing picar-x classes to the system path
# sys.path.append('RobotSource/picar-x/')
# import picarx as pix
# # importing own classes for ultrasonic sensor calibration
# sys.path.append('UltrasonicSensor/RpiUltrasonic/')
# import RpiUltrasonic as rpius
# importing own functions for mqtt connetion
sys.path.append('Network_Connections/MQTT_Connection/')
import MQTT_Receiver as mymqttr
import pandas as pd
##
   
## Block terminal for 'segs' seconds and receive data 
connection0 = mymqttr.NewMQTTReceiver("pc_lin0", segs=20)
myData = mymqttr.data
print(myData)

dfColumns = ['SampleId', 'DateTime(UTC)', 'RawDistance(cm)', 'CalibratedDistance(cm)']
dfUltrasonic = pd.DataFrame(data=myData, columns=dfColumns)
print(dfUltrasonic.head())