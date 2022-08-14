import sys
import multiprocessing as mp
import plotly.io as pio
import plotly.express as px
import pandas as pd
import os
import glob
import base64
from matplotlib import pyplot as plt
import subprocess
import time
from datetime import datetime as dtdt
import datetime as dt
from RpiSlam3 import RunSlamThread, poseQueue, RawLidarQueue, bitMapQueue

sys.path.append('Network_Connections/MongoDB_Connection')
from MDB_Connection import myMongoDB


#------------------------------- Directories ---------------------------------#
projectDir          = "/home/davidcalles/Documents/Wi-Fi-Analizer-Robot/"

wifiBashScriptDir   = "Retrieve_Wi-Fi_Data/getWiFiData.sh"
wifiDataOutputDir   = "Retrieve_Wi-Fi_Data/wifi.json"
wifiDataOutputDirCsv   = "Retrieve_Wi-Fi_Data/data.csv"

manualControlScript = 'NavigationSystem.py'

slamScript = 'RpiSlam3.py'

cameraOutput = "RetrieveVideoFeed/Pictures/"

wifiOutput = projectDir+"Retrieve_Wi-Fi_Data/Pictures/"

#-------------------------- Wifi Retrieval Variables -------------------------#
bashCommandWifi = "/bin/bash " + projectDir + wifiBashScriptDir  
wifiDataQueue = mp.Queue() 
timeDeltaWifi = dt.timedelta(seconds=4)

#-------------------------- Manual Control Variables -------------------------#
bashCommandManualControl = "/bin/python3 " + projectDir + manualControlScript  

#---------------------- LIDAR/SLAM Retrieval Variables -----------------------#
bashCommandSlam = "/bin/python3 " + projectDir + slamScript
pathToImagesSLAM = projectDir + "Wi-Fi-Analizer-Robot/SLAM/Pictures"
#-------------------------- Camera Retrieval Variables -----------------------#
cameraImgsQueue = mp.Queue() 
timeDeltaCamera = dt.timedelta(seconds=4)

#-------------------------- Syncronization variables  ------------------------#
enablePrinting = True
enableSendingData = True
processRefreshTime = 0.5 #seg
verbose = True

#----- Enables --------
enableWifiThread        = True
enableCameraThread      = True
enableSlamThread        = True
enableNavigationThread  = True
enableConsumerThread    = True

#----------------------- Video/Image Retrieval variables ---------------------#
# Command to constinusly take pictures every --timelapse milliseconds
cliCamera = "libcamera-still -t 0 " + \
           "--timelapse 1000 -p 0,0,350,350 --width 640 --height 480 --brightness 0.2 -o" + \
           projectDir + cameraOutput +"Img%d.jpg"
     
#---------------------++----- Utility Functions ------------------------------# 
def VerbosePrint(str):
    if verbose:
        print(str)

def EraseFilesFromDirectory(directoryPath):
    VerbosePrint(f"Deleting files in: {directoryPath}")
    # Path should end in '/'
    for file_name in os.listdir(directoryPath):
        # construct full file path
        file = directoryPath + file_name
        if os.path.isfile(file):
            os.remove(file)

def GetImageAsBase64(imgPath):
    with open(imgPath, "rb") as img_file:
        return base64.b64encode(img_file.read())

def GetLatestFileAndEraseOthers(folderPath):
    list_of_files = glob.glob(f"{folderPath}/*.*") # * means all if need specific format then *.csv
    mostRecenDir = max(list_of_files, key=os.path.getctime)
    time.sleep(0.2) # just make sure whoever is writting finishes
    for clean_up in list_of_files:
        if not clean_up.endswith(mostRecenDir): 
            os.remove(clean_up)
    return mostRecenDir
#----------------------------- Run Manual Control -----------------------------#    
def UpdateWifiData(bashCommand, csvPath, queue, delta):
    VerbosePrint("Started Wifi Acquisition Process")
    imgIndexWifi = 0
    tInitWifi = dtdt.now()
    try:
        while(1):
            if (dtdt.now()-tInitWifi > delta):
                tInitWifi = dtdt.now()
                imgPath = f"{wifiOutput}fig{imgIndexWifi}.jpeg"
                VerbosePrint(f"WAIFAI-File to print {imgPath}")
                
                VerbosePrint(f"WAIFAI-Enter Subprocess")
                # Fill in file with new data
                process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
                output, error = process.communicate() #uncomment for verbose
                #process.wait()
                
                # Read data - Opening JSON file and read as dict
                VerbosePrint(f"WAIFAI-Read CSV")
                wifiDf = pd.read_csv(csvPath)
                wifiDf["Signal Level Mag"] = 10**(wifiDf["Signal Level"]/20)
                fig = px.bar(wifiDf, x='SSID', y='Signal Level Mag', color='Frequency', title="Wifi-Data Magnitude and Frequency")
                #fig.show(renderer='vscode')

                #Save to image
                VerbosePrint(f"WAIFAI-Write Image")
                pio.write_image(fig, imgPath, format="jpg", width=600, height=350, engine="kaleido")
                time.sleep(0.5)
                VerbosePrint(f"WAIFAI-Enqueue image")
                # Queue image
                queue.put(GetImageAsBase64(imgPath))
                imgIndexWifi+=1
                #Do not hyper fill memory
                if(imgIndexWifi % 10 == 0):
                    GetLatestFileAndEraseOthers(wifiOutput)

            else:
                time.sleep(processRefreshTime)
    except:
        print("WAIFAI Error")
        raise KeyboardInterrupt
    
#-------------------------- Retrieve WIFI DATA Task --------------------------#    
def NavigationAlgorithm(bashCommand):
    try:
        VerbosePrint("Started Navigation Process")
        # Fill in file with new data
        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
        #Block process until finished:
        output, error = process.communicate() #uncomment for verbose 
    except:
        print("Problem running Navigation System")
        raise KeyboardInterrupt
        
#-------------------------- Retrieve LIDAR/SLAM DATA Task --------------------------#    
        
def RunSLAM(bashCommand):
        VerbosePrint("Started Slam Process")
        try:
            RunSlamThread()
        except:
            print("RunSLAM function exception")
            plt.close('all')
            raise KeyboardInterrupt
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
            
            while(poseQueue.empty() == False and enableSlamThread): # Check for robot current pose
                poseObj = poseQueue.get()
                retrievedPose  += 1
                
            while(bitMapQueue.empty() == False and enableSlamThread): # Check for slam bitmap
                bitMapObj = bitMapQueue.get()
                retrievedBitmap  += 1
            
            while(RawLidarQueue.empty() == False and enableSlamThread): # Check for raw lidar data
                rawLidarObj = RawLidarQueue.get()
                retrievedLidar  += 1
                
            while(wifiQueue.empty() == False and enableWifiThread): # Check for wifi data plot
                wifiObj = wifiQueue.get()
                retrievedWifi  += 1
            
            while(cameraQueue.empty() == False and enableCameraThread): # Check for camera pictures
                cameraObj = cameraQueue.get()
                retrievedCamera  += 1
            
            condPose    = bool(retrievedPose and enableSlamThread)
            condBitmap  = bool(retrievedBitmap and enableSlamThread)
            condLidar   = bool(retrievedLidar and enableSlamThread)
            condWifi    = bool(retrievedWifi and enableWifiThread)
            condCamera  = bool(retrievedCamera and enableCameraThread)
            
            VerbosePrint(f"Pose-{retrievedPose}, Bitmap-{retrievedBitmap}, Lidar-{retrievedLidar}, Wifi-{retrievedWifi}, Camera-{retrievedCamera}")
            if (condPose and condBitmap and condLidar and condWifi and condCamera):
                # only happens each x amount of time
                if(dtdt.now()-tInit > timeDelta):
                    VerbosePrint("CONSUMERRR-prepping data")
                    tInit = dtdt.now()
                    # Get last Slam Picture (no queue for this)
                    VerbosePrint("CONSUMERRR-Getting most recent img")
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
                        VerbosePrint("Sending data")
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
    
def SaveImage(bashCommand, cameraImgsQueue, delta):             
    try:
        VerbosePrint("Initializing libcamera-still call")
        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
        VerbosePrint("Libcamera-still Initialized")
        tInitCamera = dtdt.now()
        while(1): 
            if (dtdt.now()-tInitCamera > delta):
                tInitCamera = dtdt.now()
                VerbosePrint("Retrieving last image")
                latestImg = GetLatestFileAndEraseOthers(projectDir + cameraOutput)
                VerbosePrint(f"Erased all images but {latestImg}")
                cameraImgsQueue.put(GetImageAsBase64(latestImg))
                VerbosePrint("Queued image")
            else:
                time.sleep(processRefreshTime)    
    except:
        print("Couldnt Save Image")
        raise KeyboardInterrupt

#--------------------------------------- MAIN Task ---------------------------#

if __name__ == '__main__':
    
    VerbosePrint("Starting system")
    # New MongoDB interface object
    mdbObj = myMongoDB() # CHANGE URL HERE: args{url, dbName,'SampleCollection0'}

    # ---- CREATE POOL OF PROCESSES -----
    num_workers = 5 # Listed below
    pool = mp.Pool(processes=num_workers)
    
    # Create processes WIFI
    if enableWifiThread:
        pool.apply_async(UpdateWifiData, args = (bashCommandWifi, projectDir+wifiDataOutputDirCsv, wifiDataQueue, timeDeltaWifi))
        VerbosePrint("Created Wifi Data Process")
    # Create Process MANUAL CONTROL
    if enableNavigationThread:  
        pool.apply_async(NavigationAlgorithm, args = (bashCommandManualControl,))
        VerbosePrint("Created Navigation Data Process")
    # Create SLAM process
    if enableSlamThread:
        pool.apply_async(RunSLAM, args = (bashCommandSlam,))
        VerbosePrint("Created SLAM Process")
    # Camera Thread
    if enableCameraThread:
        pool.apply_async(SaveImage, args = (cliCamera, cameraImgsQueue, timeDeltaCamera))
        VerbosePrint("Created Camera Capture Process")
    # Consume-Plot SLAM results
    if enableConsumerThread:
        pool.apply_async(ConsumeData, args = (poseQueue, bitMapQueue, RawLidarQueue, wifiDataQueue, cameraImgsQueue, mdbObj))
        VerbosePrint("Created Data Consumption Process")
    
    while(1):
        
        # Take picture from camera
        try:
            time.sleep(5)
            VerbosePrint("Running Loop Running")

        except:
            print("keyboard Exception Main Loop")
            plt.close('all')
            pool.close()
            pool.join()
            exit(0)
        