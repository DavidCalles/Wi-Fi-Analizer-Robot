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

cameraOutputAbs = projectDir+cameraOutput
wifiOutputAbs = projectDir+"Retrieve_Wi-Fi_Data/Pictures/"
slamOutputAbs = projectDir + "SLAM/Pictures/"


#-------------------------- Wifi Retrieval Variables -------------------------#
bashCommandWifi = "/bin/bash " + projectDir + wifiBashScriptDir  
wifiDataQueue = mp.Queue() 
timeDeltaWifi = dt.timedelta(seconds=4)
imgIndexWifi = 0
tInitWifi = dtdt.now()

#-------------------------- Manual Control Variables -------------------------#
bashCommandManualControl = "/bin/python3 " + projectDir + manualControlScript  

#---------------------- LIDAR/SLAM Retrieval Variables -----------------------#
bashCommandSlam = "/bin/python3 " + projectDir + slamScript

#-------------------------- Camera Retrieval Variables -----------------------#
cameraImgsQueue = mp.Queue() 
timeDeltaCamera = dt.timedelta(seconds=4)
tInitCamera = dtdt.now()

#-------------------------- Syncronization variables  ------------------------#
enablePrinting = True
enableSendingData = False
processRefreshTime = 0.2 #seg
verbose = True
timeDeltaConsumer = dt.timedelta(seconds=5)
settlingTime = 1  #seg

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
           projectDir + cameraOutput +"Img%d.jpg >/dev/null 2>/dev/null"
     
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
    global tInitWifi
    global imgIndexWifi
    try:
        if (dtdt.now()-tInitWifi > delta):
            tInitWifi = dtdt.now()
            imgPath = f"{wifiOutputAbs}fig{imgIndexWifi}.jpeg"
            
            VerbosePrint(f"WAIFAI-Enter Subprocess")
            # Fill in file with new data
            process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
            #output, error = process.communicate() #uncomment for verbose
            process.wait()
            #time.sleep(0.5)
            
            # Read data - Opening JSON file and read as dict
            VerbosePrint(f"WAIFAI-Read CSV")
            wifiDf = pd.read_csv(csvPath)
            VerbosePrint(f"WAIFAI- Succesfully Read CSV")
            wifiDf["Signal Level Mag"] = 10**(wifiDf["Signal Level"]/20)
            figWF = px.bar(wifiDf, x='SSID', y='Signal Level Mag', color='Frequency', title="Wifi-Data Magnitude and Frequency")
            #figWF.show(renderer='vscode')

            #Save to image
            VerbosePrint(f"WAIFAI-Write to Image: {imgPath}")
            pio.write_image(figWF, imgPath, format="jpg", width=600, height=350, engine="kaleido")
            time.sleep(0.2)
            VerbosePrint(f"WAIFAI-Enqueue image")
            # Queue image
            queue.put(GetImageAsBase64(imgPath))
            imgIndexWifi+=1
            #Do not hyper fill memory
            if(imgIndexWifi % 10 == 0):
                GetLatestFileAndEraseOthers(wifiOutputAbs)

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

#-------------------------- Data SENDING Task --------------------------# 
def ConsumeData(poseQueue, bitMapQueue, RawLidarQueue, wifiQueue, cameraQueue, timeDelta, mdbObj=None):
    retrievedBitmap = 0
    retrievedLidar = 0
    retrievedPose = 0
    retrievedWifi = 0
    retrievedCamera = 0
    packetSentCount = 0
    tInit = dtdt.now()
    
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
                        
            if(dtdt.now()-tInit > timeDelta):  
                tInit = dtdt.now()
                VerbosePrint("Attempting to send")
                VerbosePrint(f"Pose-{retrievedPose}, Bitmap-{retrievedBitmap}, Lidar-{retrievedLidar}, Wifi-{retrievedWifi}, Camera-{retrievedCamera}")
                condPose    = bool(retrievedPose and enableSlamThread)
                condBitmap  = bool(retrievedBitmap and enableSlamThread)
                condLidar   = bool(retrievedLidar and enableSlamThread)
                condWifi    = bool(retrievedWifi and enableWifiThread)
                condCamera  = bool(retrievedCamera and enableCameraThread) 
                
                # Get last Slam Picture (no queue for this)
                VerbosePrint("CONSUMERRR-Getting most recent img")
                latestSlamPicPath = GetLatestFileAndEraseOthers(slamOutputAbs)
                slamImgObj = GetImageAsBase64(latestSlamPicPath)

                if (condPose and condBitmap and condLidar and condWifi and condCamera):
                    
                    if enablePrinting:
                        print("#-----------------------------------------------------------#")
                        print(f"#-------------- NEW SAMPLE {packetSentCount} ------------------#")
                        print("#-----------------------------------------------------------#")
                        print(f"DateTime: {tInit}")
                        print(f"Pose: {poseObj}")
                        print(f"Size of Bitmap: {sys.getsizeof(bitMapObj)/1024} kB")
                        print(f"Size of Lidar Data: {sys.getsizeof(rawLidarObj)/1024} kB")
                        print(f"Size of Wifi Plot:{sys.getsizeof(wifiObj)/1024} kB")
                        print(f"Size of Camera Pic:{sys.getsizeof(cameraObj)/1024} kB")
                        print(f"Size of SLAM Pic:{sys.getsizeof(slamImgObj)/1024} kB")
                        print("#-----------------------------------------------------------#")
                        print(f"#-------------- END SAMPLE {packetSentCount} ------------------#")
                        print("#-----------------------------------------------------------#")
                    
                    if (enableSendingData):  
                        # Send images as string (eliminate b'')
                        newPacket = {"TimeStamp":time.time(),
                                    "SampleCount":packetSentCount,
                                    "ImgCam":str(cameraObj)[2:-1],
                                    "ImgWifi":str(wifiObj)[2:-1],
                                    "ImgSlam":str(slamImgObj)[2:-1]}    
                        VerbosePrint("Sending data")
                        # Send data to Mongodb server
                        mdbObj.SendPacket(newEntry=newPacket)

                    packetSentCount += 1
                    # Reset all flags
                    retrievedBitmap = 0
                    retrievedLidar = 0
                    retrievedPose = 0
                    retrievedWifi = 0
                    retrievedCamera = 0
            else:
                time.sleep(processRefreshTime) 
    except:
        print("Consumer Error")
        raise KeyboardInterrupt
    
#-------------------------- Camera Acquisition Task --------------------------# 
def SaveImage(cameraImgsQueue, delta):
    global tInitCamera           
    try:
        if (dtdt.now()-tInitCamera > delta):
            tInitCamera = dtdt.now()
            VerbosePrint("CAMERAA - Retrieving last image")
            latestImg = GetLatestFileAndEraseOthers(projectDir + cameraOutput)
            VerbosePrint(f"CAMERAA - Erased all images but {latestImg}")
            cameraImgsQueue.put(GetImageAsBase64(latestImg))
            VerbosePrint("CAMERAA  - Queued image")
        else:
            time.sleep(processRefreshTime)    
    except:
        print("CAMERAA - Couldnt Save Image")
        raise KeyboardInterrupt

#-------------------------- Update Camera and Wifi Task --------------------------# 

def UpdateCameraAndWifi(cameraArgs, wifiArgs):
    VerbosePrint("WIFI-CAM Initializing libcamera-still call")
    VerbosePrint("WIFI-CAM Libcamera-still Initialized")
    VerbosePrint("WIFI-CAM Started Wifi Acquisition Process")
    processCamera = subprocess.Popen(cameraArgs[0].split(), stdout=subprocess.PIPE)
    while(1):
        SaveImage(cameraArgs[1], cameraArgs[2])
        UpdateWifiData(wifiArgs[0], wifiArgs[1], wifiArgs[2], wifiArgs[3])

#--------------------------------------- MAIN Task ---------------------------#

if __name__ == '__main__':
    
    VerbosePrint("Starting system")
    # Erasing past images
    EraseFilesFromDirectory(wifiOutputAbs)
    EraseFilesFromDirectory(cameraOutputAbs)
    EraseFilesFromDirectory(slamOutputAbs)
    # New MongoDB interface object
    mdbObj = myMongoDB( url='mongodb+srv://kjaskaran:QGx6rTpqiM11prDj@clusterjk.z1qwasf.mongodb.net/?retryWrites=true&w=majority', 
                        dbName='test',
                        collectName='wivibots')
    # ---- CREATE PROCESSES -----
    wifiCam_P = mp.Process(target=UpdateCameraAndWifi,
                args = ([cliCamera, cameraImgsQueue, timeDeltaCamera],
                        [bashCommandWifi, projectDir+wifiDataOutputDirCsv, wifiDataQueue, timeDeltaWifi]))
    manualNav_P = mp.Process(target=NavigationAlgorithm, args=(bashCommandManualControl,))
    slam_consume = mp.Process(target=ConsumeData, args=(poseQueue, bitMapQueue, RawLidarQueue, wifiDataQueue, cameraImgsQueue, timeDeltaConsumer, mdbObj))
    slam_P = mp.Process(target=RunSLAM, args=(bashCommandSlam,))
    

    # Create processes WIFI-Cam
    if (enableWifiThread and enableCameraThread):
        wifiCam_P.start()
        VerbosePrint("Created Wifi-CAM Data Process")
        time.sleep(settlingTime)
    # Create Process MANUAL CONTROL
    if enableNavigationThread:  
        manualNav_P.start() # Run manual navigation
        VerbosePrint("Created Navigation Data Process")
        time.sleep(settlingTime)
    # Create SLAM process
    if enableSlamThread:
        slam_P.start()
        VerbosePrint("Created SLAM Process")
        time.sleep(settlingTime)
    # Consume-Plot SLAM results
    if enableConsumerThread:
        slam_consume.start()
        VerbosePrint("Created Data Consumption Process")
        time.sleep(settlingTime)
    
    while(1):
        
        # Take picture from camera
        try:
            time.sleep(5)
            VerbosePrint("Running Loop Running")

        except:
            print("keyboard Exception Main Loop")
            wifiCam_P.terminate()
            manualNav_P.terminate()
            slam_P.terminate()
            slam_consume.terminate()
            exit(0)
        