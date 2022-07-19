import multiprocessing as mp
import queue
import pandas
import json
import subprocess
import time
from RpiSlam import *

#------------------------------- Directories ---------------------------------#
projectDir          = "/home/davidcalles/Documents/Wi-Fi-Analizer-Robot/"

wifiBashScriptDir   = "Retrieve_Wi-Fi_Data/getWiFiData.sh"
wifiDataOutputDir   = "Retrieve_Wi-Fi_Data/wifi.json"

manualControlScript = "ManualNavigation2.py"

#-------------------------- Wifi Retrieval Variables -------------------------#
bashCommandWifi = "/bin/bash " + projectDir + wifiBashScriptDir  
WifiDataQueue = mp.Queue() 

#-------------------------- Manual Control Variables -------------------------#
bashCommandManualControl = "/bin/python3 " + projectDir + manualControlScript  

#---------------------- LIDAR/SLAM Retrieval Variables -----------------------#
poseQueue = mp.Queue() 
bitMapQueue = mp.Queue()  
RawLidarQueue = mp.Queue()  

#------------------------------- Sample Task ---------------------------------#
def f(l, i):
    while(1):
        l.acquire()
        try:
            print('hello world', i)
        finally:
            l.release()
            time.sleep(2)
     
#-------------------------- Run Manual Control --------------------------#    
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
def RunManualControl(bashCommand):
    print("Started Navigation Process")
    while(1):
        # Fill in file with new data
        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
        output, error = process.communicate() #uncomment for verbose      
        
#-------------------------- Retrieve LIDAR/SLAM DATA Task --------------------------#    
def RunSLAM(poseQueue, bitMapQueue, RawLidarQueue):
        print("Started Slam Process")
        slam_compute(poseQueue, bitMapQueue, RawLidarQueue)


def ConsumeSLAM(poseQueue, bitMapQueue, RawLidarQueue):
    if poseQueue.empty() == False:
        poseObj = poseQueue.get(pose)
        print("Pose: ")
        print(poseObj)
       
    if bitMapQueue.empty() == False:
        bitMapObj = bitMapQueue.get(bitMapQueue)
        print(len(bitMapObj))
    
    if RawLidarQueue.empty() == False:
        radLidarObj = RawLidarQueue.get([distances, angles, quality])
        print(len(radLidarObj))
        
#--------------------------------------- MAIN Task ---------------------------#

if __name__ == '__main__':

    # Create processes WIFI
    wifi_P = mp.Process(target=UpdateWifiData, args=(bashCommandWifi, projectDir+wifiDataOutputDir, WifiDataQueue))
    wifi_P.start()
    # Create Process MANUAL CONTROL
    manualNav_P = mp.Process(target=RunManualControl, args=(bashCommandManualControl,))
    manualNav_P.start() # Run manual navigation
    # Create SLAM process
    slam_P = mp.Process(target=RunSLAM, args=(poseQueue, bitMapQueue, RawLidarQueue))
    slam_P.start()
    
    while(1):
        
        # Get data from wifi data queue
        try:
            wifiObj = WifiDataQueue.get(block=True, timeout=6)
            print(json.dumps(wifiObj, indent=4, sort_keys=True))  
            
            ConsumeSLAM(poseQueue, bitMapQueue, RawLidarQueue)

        except queue.Empty:
            print("Couldnt find new wifi data")
            exit(0) 
        
        except KeyboardInterrupt:
            runThread = False
            wifi_P.join()
            manualNav_P.join()
            slam_P.join()
            lidar.stop()
            lidar.disconnect()
            exit(0)         
        