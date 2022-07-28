# importing sys
import sys

# importing own functions for mqtt connetion
sys.path.append('C:/Users/yodav/OneDrive/Documents/Conestoga_College/FOURTH_TERM/Capstone_Project/Wi_Fi_Analizer_Robot/Network_Connections/MQTT_Connection')
import MQTT_Receiver_HTTP as mymqttr

sys.path.append('C:/Users/yodav/OneDrive/Documents/Conestoga_College/FOURTH_TERM/Capstone_Project/Wi_Fi_Analizer_Robot/Network_Connections/HTTP_Connection')
from restApi import sampleUrl, sampleTopic, getRequestJSON 
import pandas as pd
import numpy as np
import plotly.express as px
import json
##
   
## Block terminal for 'segs' seconds and receive data 
connection0 = mymqttr.NewMQTTReceiver("pc_lin0", segs=10)
connection0.disconnect()
myData = mymqttr.data

# Turn data to a dataframe
dfColumns = ['SampleId', 'DateTime(UTC)', 'RawDistance(cm)', 'CalibratedDistance(cm)']
dfUltrasonic = pd.DataFrame(data=myData, columns=dfColumns)
dfUltrasonic = dfUltrasonic.astype({'SampleId': 'int32', 'RawDistance(cm)':'datetime64',
                                    'RawDistance(cm)': 'float64', 'CalibratedDistance(cm)': 'float'})
#print(dfUltrasonic.info())
print("\n", dfUltrasonic.head())

# Analytics 
print("\n/*----------------------- ANALYTICS --------------------------*/\n")
print(f"Received samples: {len(dfUltrasonic['SampleId'])}")
missingSamples = np.count_nonzero(np.absolute(np.diff(dfUltrasonic['SampleId'].to_numpy())) > 1)
print(f"Lost samples: {missingSamples}")
print("Statistics:\n")
print(dfUltrasonic.describe())
# Write data to json
jsonPath = "UltrasonicSensor/RobotUltraSensor/testData.json"
dfUltrasonic.to_json(jsonPath, orient='records', indent=2)

# Plot
fig = px.line(dfUltrasonic, x="DateTime(UTC)",
              y=["RawDistance(cm)", "CalibratedDistance(cm)"],
              title='Ultrasensor Data', template='plotly_dark')
fig.show()

# GET request
print(f"Output from {sampleUrl+sampleTopic}:")
response = getRequestJSON(sampleUrl+sampleTopic)
print(json.dumps(response, indent=4, sort_keys=True))