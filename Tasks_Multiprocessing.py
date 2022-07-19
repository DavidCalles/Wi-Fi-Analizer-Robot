import multiprocessing as mp
import queue
import pandas
import json
import subprocess
import time

#------------------------------- Directories ---------------------------------#
projectDir          = "/home/davidcalles/Documents/Wi-Fi-Analizer-Robot/"
wifiBashScriptDir   = "Retrieve_Wi-Fi_Data/getWiFiData.sh"
wifiDataOutputDir   = "Retrieve_Wi-Fi_Data/wifi.json"

#-------------------------- Wifi Retrieval Variables -------------------------#
bashCommandWifi = "/bin/bash " + projectDir + wifiBashScriptDir  
WifiDataQueue = mp.Queue() 

#------------------------------- Sample Task ---------------------------------#
def f(l, i):
    while(1):
        l.acquire()
        try:
            print('hello world', i)
        finally:
            l.release()
            time.sleep(2)
     
#-------------------------- Retrieve WIFI DATA Task --------------------------#    
def UpdateWifiData(bashCommand, jsonPath, queue):
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
        time.sleep(2)
            
            
#--------------------------------------- MAIN Task ---------------------------#

if __name__ == '__main__':

    # Create processes
    wifi_P = mp.Process(target=UpdateWifiData, args=(bashCommandWifi, projectDir+wifiDataOutputDir, WifiDataQueue))
    wifi_P.start()
    
    while(1):
        
        # Get data from wifi data queue
        try:
            wifiObj = WifiDataQueue.get(block=True, timeout=6)
            print(json.dumps(wifiObj, indent=4, sort_keys=True))  
              
        except queue.Empty:
            print("Couldnt find new wifi data")
            exit(1)    
        
    wifi_P.join()