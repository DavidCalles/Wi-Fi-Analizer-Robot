import sys
import imageio as iio
import base64
from datetime import datetime as dtdt
import time

 
# read an image
sys.path.append('Network_Connections/MongoDB_Connection')
from MDB_Connection import myMongoDB

def GetImageAsBase64(imgPath):
    with open(imgPath, "rb") as img_file:
        return base64.b64encode(img_file.read())

newConnect = myMongoDB( url='mongodb+srv://kjaskaran:QGx6rTpqiM11prDj@clusterjk.z1qwasf.mongodb.net/?retryWrites=true&w=majority', 
                        dbName='test',
                        collectName='wivibots')

data = {"TimeStamp":time.time()}
imgPathWifi = "/home/davidcalles/Documents/Wi-Fi-Analizer-Robot/Retrieve_Wi-Fi_Data/Pictures/fig32.jpeg"
imgPathCam = "/home/davidcalles/Documents/Wi-Fi-Analizer-Robot/RetrieveVideoFeed/Pictures/Img145.jpg"
imgPathSlam = "/home/davidcalles/Documents/Wi-Fi-Analizer-Robot/SLAM/Pictures/slamMap-10-37-43.png"

data["ImgWifi"] = str(GetImageAsBase64(imgPathWifi))[2:-1]
data["ImgCam"] = str(GetImageAsBase64(imgPathCam))[2:-1]
data["ImgSlam"] = str(GetImageAsBase64(imgPathSlam))[2:-1]

newConnect.SendPacket(data)
