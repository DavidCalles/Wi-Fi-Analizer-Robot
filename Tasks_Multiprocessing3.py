import sys
import multiprocessing as mp
import plotly.io as pio
import plotly.express as px
import pandas as pd
import os
import glob
import base64
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

wifiOutput = projectDir+"Retrieve_Wi-Fi_Data/Pictures/"

#-------------------------- Wifi Retrieval Variables -------------------------#
bashCommandWifi = "/bin/bash " + projectDir + wifiBashScriptDir  
wifiDataQueue = mp.Queue() 

#-------------------------- Manual Control Variables -------------------------#
bashCommandManualControl = "/bin/python3 " + projectDir + manualControlScript  

#---------------------- LIDAR/SLAM Retrieval Variables -----------------------#
bashCommandSlam = "/bin/python3 " + projectDir + slamScript
pathToImagesSLAM = projectDir + "Wi-Fi-Analizer-Robot/SLAM/Pictures"
#-------------------------- Camera Retrieval Variables -----------------------#
cameraImgsQueue = mp.Queue() 

#-------------------------- Syncronization variables  ------------------------#
enablePrinting = True
enableSendingData = True

#----------------------- Video/Image Retrieval variables ---------------------#
imageIndex = 0
#cliCamera = "libcamera-still -t 0 " + \
#            "--timelapse 3000 -p 0,0,350,350 --width 640 --height 480 --brightness 0.2 -o" + \
#            projectDir + cameraOutput +"Img%d.jpg"

#cliCamera = f"libcamera-jpeg -t 3000 -p 0,0,350,350 --width 640 --height 480 --brightness 0.2 -o {projectDir}{cameraOutput}"
cliCamera = f"libcamera-still --nopreview -o {projectDir}{cameraOutput}"
     
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
def UpdateWifiData(bashCommand, csvPath, outputPath, queue):
    print("Started Wifi Acquisition Process")
    imgIndex = 0
    try:
        while(1):
            # Erase file contents
            f = open(outputPath, 'r+')
            f.truncate(0)
            f.close()
            
            # Fill in file with new data
            process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
            output, error = process.communicate() #uncomment for verbose
            process.wait()
            
            # Read data - Opening JSON file and read as dict
            wifiDf = pd.read_csv(csvPath)
            wifiDf["Signal Level Mag"] = 10**(wifiDf["Signal Level"]/20)
            fig = px.bar(wifiDf, x='SSID', y='Signal Level Mag', color='Frequency', title="Wifi-Data Magnitude and Frequency")
            #fig.show()

            #Save to image
            imgPath = f"{projectDir}Retrieve_Wi-Fi_Data/Pictures/fig{imgIndex}.jpeg"
            fig.write_image(imgPath)
            imgIndex+=1
            queue.put(GetImageAsBase64(imgPath))
            time.sleep(3)
    except:
        print("Wifi Error")
        raise KeyboardInterrupt
#----------------------------- Helper Functions -------------------------------# 
def GetImageAsBase64(imgPath):
    with open(imgPath, "rb") as img_file:
        return base64.b64encode(img_file.read())

def GetLatestFileAndEraseOthers(folderPath):
    list_of_files = glob.glob(f"{folderPath}/*.*") # * means all if need specific format then *.csv
    mostRecenDir = max(list_of_files, key=os.path.getctime)
    for clean_up in list_of_files:
        if not clean_up.endswith(mostRecenDir): 
            os.remove(clean_up)
    return mostRecenDir
    
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


def ConsumeData(poseQueue, bitMapQueue, RawLidarQueue, wifiQueue, cameraQueue, mdbObj=None):
    retrievedBitmap = 0
    retrievedLidar = 0
    retrievedPose = 0
    retrievedWifi = 0
    retrievedCamera = 0
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
                
            while(wifiQueue.empty() == False): # Check for wifi data plot
                wifiObj = wifiQueue.get()
                retrievedWifi  += 1
            
            while(cameraQueue.empty() == False): # Check for wifi data plot
                cameraObj = cameraQueue.get()
                retrievedCamera  += 1
            
            if (retrievedBitmap and retrievedPose and retrievedLidar and retrievedWifi and retrievedCamera):
                if(dtdt.now()-tInit > timeDelta):
                    tInit = dtdt.now()
                    # Get last Slam Picture
                    latestSlamPicPath = GetLatestFileAndEraseOthers(pathToImagesSLAM)
                    slamImgObj = GetImageAsBase64(latestSlamPicPath)

                    if enablePrinting:
                        print(f"DateTime: {tInit}")
                        print(f"Pose: {poseObj}")
                        print(f"Size of Bitmap: {len(bitMapObj)}")
                        print(f"Size of Lidar Data: {len(rawLidarObj)}")
                        print(f"Size of Wifi Plot:{len(wifiObj)}")
                        print(f"Size of Camera Pic:{len(cameraObj)}")
                        print(f"Size of Camera Pic:{len(slamImgObj)}")
                    
                    if (enableSendingData):  
                        newPacket = {"CamImg":cameraObj, "WifiImg":wifiObj, "SlamImg":slamImgObj}    
                        print("Sending data")
                        # Send data to Mongodb server
                        # mdbObj.SendPacket(newEntry={
                        #     'pose':poseObj, 'rawScan':radLidarObj
                        # })
                    # Reset all flags
                    retrievedBitmap = 0
                    retrievedLidar = 0
                    retrievedPose = 0
                    retrievedWifi = 0
                    retrievedCamera = 0
                
    except:
        print("Consumer Error")
        raise KeyboardInterrupt
    
def SaveImage(bashCommand, cameraImgsQueue): 
    global imageIndex
    newImageName = "img"+str(imageIndex)+".jpg"
    Path(cameraOutput+newImageName).touch()
    newImageCommand = bashCommand + newImageName
    imageIndex += 1
    # Fill in file with new data
    process = subprocess.Popen(newImageCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate() #uncomment for verbose  
    process.wait()
    cameraImgsQueue.put(GetImageAsBase64(f"{projectDir}{cameraOutput}{newImageName}"))


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
    slam_consume = mp.Process(target=ConsumeData, args=(poseQueue, bitMapQueue, RawLidarQueue, wifiDataQueue, cameraImgsQueue, mdbObj))
    slam_consume.start()
    print("Created Data Consumption Process")
    
    while(1):
        
        # Take picture from camera
        try:
            SaveImage(cliCamera) 
            print("While Loop Running")
            time.sleep(3) 

        except:
            print("keyboard Exception Main Loop")
            wifi_P.terminate()
            manualNav_P.terminate()
            slam_P.terminate()
            slam_consume.terminate()
            exit(0)
        