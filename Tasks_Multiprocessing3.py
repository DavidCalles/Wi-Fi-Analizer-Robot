import sys
import multiprocessing as mp
import queue
import pandas
import os
import json
import subprocess
import time
from datetime import datetime as dtdt
import datetime as dt
from RpiSlam3 import RunSlamThread, poseQueue, RawLidarQueue, bitMapQueue
from pathlib import Path

sys.path.append('Network_Connections/MongoDB_Connection')
from MDB_Connection import myMongoDB


#------------------------------- Directories ---------------------------------#
projectDir          = "/home/davidcalles/Documents/Wi-Fi-Analizer-Robot/"

wifiBashScriptDir   = "Retrieve_Wi-Fi_Data/getWiFiData.sh"
wifiDataOutputDir   = "Retrieve_Wi-Fi_Data/wifi.json"

manualControlScript = 'NavigationSystem.py'

slamScript = 'RpiSlam3.py'#'SLAM/SLAM-on-Raspberry-Pi/rpslam-thread.py'

cameraOutput = "RetrieveVideoFeed/Pictures/"

#-------------------------- Wifi Retrieval Variables -------------------------#
bashCommandWifi = "/bin/bash " + projectDir + wifiBashScriptDir  
wifiDataQueue = mp.Queue() 

#-------------------------- Manual Control Variables -------------------------#
bashCommandManualControl = "/bin/python3 " + projectDir + manualControlScript  

#---------------------- LIDAR/SLAM Retrieval Variables -----------------------#
bashCommandSlam = "/bin/python3 " + projectDir + slamScript

#-------------------------- Syncronization variables  ------------------------#
enablePrinting = True
enableSendingData = True


#----------------------- Video/Image Retrieval variables ---------------------#
imageIndex = 0
cliCamera = "libcamera-still --nopreview -o" + projectDir + cameraOutput
     
#---------------------++----- Utility Functions ------------------------------# 

def EraseFilesFromDirectory(directoryPath):
    # Path should end in '/'
    for file_name in os.listdir(directoryPath):
        # construct full file path
        file = directoryPath + file_name
        if os.path.isfile(file):
            print('Deleting file:', file)
            os.remove(file)
#----------------------------- Run Manual Control -----------------------------#    
def UpdateWifiData(bashCommand, jsonPath, queue):
    print("Started Wifi Acquisition Process")
    while(1):
        # Erase file contents
        f = open(jsonPath, 'r+')
        f.truncate(0)
        f.close()
        
        # Fill in file with new data
        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
        output, error = process.communicate() #uncomment for verbose
        
        # Read data - Opening JSON file and read as dict
        f = open(jsonPath)
        data = json.load(f)
        queue.put(data)
        f.close()
        time.sleep(3)
            
#-------------------------- Retrieve WIFI DATA Task --------------------------#    
def NavigationAlgorithm(bashCommand):
    print("Started Navigation Process")
    while(1):
        # Fill in file with new data
        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
        output, error = process.communicate() #uncomment for verbose  
        
#-------------------------- Retrieve LIDAR/SLAM DATA Task --------------------------#    
        
def RunSLAM(bashCommand):
        print("Started Slam Process")
        RunSlamThread()
        # Fill in file with new data
        # process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
        # output, error = process.communicate() #uncomment for verbose  


def ConsumeSLAM(poseQueue, bitMapQueue, RawLidarQueue, wifiQueue, mdbObj=None):
    retrievedBitmap = 0
    retrievedLidar = 0
    retrievedPose = 0
    retrievedWifi = 0
    tInit = dtdt.now()
    timeDelta = dt.timedelta(seconds=1)
    
    try:
        while(1):
            
            while(poseQueue.empty() == False): # Check for robot current pose
                poseObj = poseQueue.get()
                retrievedBitmap  += 1
                
            while(bitMapQueue.empty() == False): # Check for slam bitmap
                bitMapObj = bitMapQueue.get()
                retrievedPose  += 1
            
            while(RawLidarQueue.empty() == False): # Check for raw lidar data
                rawLidarObj = RawLidarQueue.get()
                retrievedLidar  += 1
                
            while(wifiQueue.empty() == False): # Check for slam bitmap
                wifiObj = wifiQueue.get()
                retrievedWifi  += 1
            
            if retrievedBitmap and retrievedPose and retrievedLidar and retrievedWifi:
                if(dtdt.now()-tInit > timeDelta):
                    tInit = dtdt.now()              
                    if enablePrinting:
                        print(f"DateTime: {tInit}")
                        print(f"Pose: {poseObj}")
                        print(f"Size of Bitmap: {len(bitMapObj)}")
                        print(f"Size of Lidar Data: {len(rawLidarObj)}")
                        print("Wifi Data:")
                        print(json.dumps(wifiObj, indent=4, sort_keys=True))
                    
                    if (enableSendingData):      
                        print("Sending data")
                        # Send data to Mongodb server
                        # mdbObj.SendPacket(newEntry={
                        #     'pose':poseObj, 'rawScan':radLidarObj
                        # })
                
    except:
        print("Consumer Error")
        raise KeyboardInterrupt
    
def SaveImage(bashCommand): 
    global imageIndex
    newImageName = "img"+str(imageIndex)+".jpg"
    Path(cameraOutput+newImageName).touch()
    newImageCommand = bashCommand + newImageName
    imageIndex += 1
    # Fill in file with new data
    process = subprocess.Popen(newImageCommand.split(), stdout=subprocess.PIPE)
    #output, error = process.communicate() #uncomment for verbose            
#--------------------------------------- MAIN Task ---------------------------#

if __name__ == '__main__':
    
    print("Starting system")
    # New MongoDB interface object
    mdbObj = myMongoDB() # CHANGE URL HERE: args{url, dbName,'SampleCollection0'}
    # Plot setup
    # Create processes WIFI
    wifi_P = mp.Process(target=UpdateWifiData, args=(bashCommandWifi, projectDir+wifiDataOutputDir, wifiDataQueue))
    wifi_P.start()
    print("Created Wifi Data Process")
    # Create Process MANUAL CONTROL
    manualNav_P = mp.Process(target=NavigationAlgorithm, args=(bashCommandManualControl,))
    manualNav_P.start() # Run manual navigation
    print("Created Navigation Data Process")
    # Create SLAM process
    slam_P = mp.Process(target=RunSLAM, args=(bashCommandSlam,))
    slam_P.start()
    print("Created SLAM Process")
    # Consume-Plot SLAM results
    slam_consume = mp.Process(target=ConsumeSLAM, args=(poseQueue, bitMapQueue, RawLidarQueue, wifiDataQueue, mdbObj))
    slam_consume.start()
    print("Created Data Consumption Process")
    
    while(1):
        
        # Take picture from camera
        try:
            SaveImage(cliCamera) 
            print("While Loop Running")
            time.sleep(1) 

        except:
            print("keyboard Exception Main Loop")
            wifi_P.terminate()
            manualNav_P.terminate()
            slam_P.terminate()
            slam_consume.terminate()
            exit(0)         
        