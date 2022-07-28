import importlib.util as imp  
rootDirectory = "C:/Users/yodav/OneDrive/Documents/Conestoga_College/FOURTH_TERM/Capstone_Project/Wi_Fi_Analizer_Robot/Network_Connections"
spec1 = imp.spec_from_file_location("MQTT_Receiver_MongoDB", rootDirectory+"/MQTT_Connection/MQTT_Receiver_MongoDB.py")
mqtt = imp.module_from_spec(spec1)      
spec1.loader.exec_module(mqtt)
rootDirectory2 = "C:/Users/yodav/OneDrive/Documents/Conestoga_College/FOURTH_TERM/Capstone_Project/Wi_Fi_Analizer_Robot/Network_Connections/MongoDB_Connection"
spec2 = imp.spec_from_file_location("MDB_Connection", rootDirectory2+"/MDB_Connection.py")
mdb = imp.module_from_spec(spec2)      
spec2.loader.exec_module(mdb)

import pandas as pd
import numpy as np
import plotly.express as px
import json
##
   
## Block terminal for 'segs' seconds and receive data 
connection0 = mqtt.NewMQTTReceiver("pc_lin0", segs=10)
connection0.disconnect()
myData = connection0.getData()

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

#Plot
# fig = px.line(dfUltrasonic, x="DateTime(UTC)",
#               y=["RawDistance(cm)", "CalibratedDistance(cm)"],
#               title='Ultrasensor Data', template='plotly_dark')
# fig.show()

# MongoDB request
mymongoClient = mdb.myMongoDB(dbName=mqtt.mongoDbName, collectName=mqtt.mongoCollectName)
mymongoClient.GetCollection()