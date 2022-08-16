import sys
import base64
from datetime import datetime as dtdt
import time
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
 
# read an image
sys.path.append('Network_Connections/MongoDB_Connection')
from MDB_Connection import myMongoDB

mainDir = "C:\\Users\\yodav\\OneDrive\\Documents\\Conestoga_College\\FOURTH_TERM\\Capstone_Project\\Wi_Fi_Analizer_Robot\\"

def GetImageAsBase64(imgPath):
    with open(imgPath, "rb") as img_file:
        return base64.b64encode(img_file.read())

newConnect = myMongoDB( url='mongodb+srv://kjaskaran:QGx6rTpqiM11prDj@clusterjk.z1qwasf.mongodb.net/?retryWrites=true&w=majority', 
                        dbName='test',
                        collectName='wivibots')

imgPathWifi = mainDir+"Retrieve_Wi-Fi_Data\\Pictures\\fig0.jpeg"
imgPathCam = mainDir+"RetrieveVideoFeed\\Pictures\\Img30.jpg"
imgPathSlam = mainDir+"SLAM\\Pictures\\slamMap-17-56-18.png"
count = 0

# f = plt.figure()
# img1 = mpimg.imread(imgPathWifi)
# imgplot1 = plt.imshow(img1)
# f.show()

# g = plt.figure()
# img2 = mpimg.imread(imgPathCam)
# imgplot2 = plt.imshow(img2)
# g.show()

# h = plt.figure()
# img3 = mpimg.imread(imgPathSlam)
# imgplot3 = plt.imshow(img3)
# h.show()

# plt.show()

while(1):
    
    data = {"TimeStamp":time.time(), "SampleCount":count}
    data["ImgWifi"] = str(GetImageAsBase64(imgPathWifi))[2:-1]
    data["ImgCam"] = str(GetImageAsBase64(imgPathCam))[2:-1]
    data["ImgSlam"] = str(GetImageAsBase64(imgPathSlam))[2:-1]
    
    if(count<10):
        print(f"Packet Sent {count}")
        newConnect.DeleteOlder(minutes=10)
        newConnect.SendPacket(data)
    else:
        print(type(newConnect.GetCollectionNoPrint()))
    
    count+=1
    time.sleep(10)

#newConnect.DeleteAll()
