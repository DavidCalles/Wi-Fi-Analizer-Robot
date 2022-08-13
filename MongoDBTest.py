import sys
import imageio as iio
 
# read an image
sys.path.append('Network_Connections/MongoDB_Connection')
from MDB_Connection import myMongoDB

newConnect = myMongoDB( url='mongodb+srv://kjaskaran:QGx6rTpqiM11prDj@clusterjk.z1qwasf.mongodb.net/?retryWrites=true&w=majority', 
                        dbName='wivibot',
                        collectName='wivibots')

data = {"Data0":"u suck", "Data1": "U suck harder"}
imgPath = "SLAM/Pictures/slamMap-09-31-42.png"
newConnect.AddImageBinary(imgPath, data, field="img0")

newConnect.SendPacket(data)
#newConnect.SendImage("SLAM/Pictures/slamMap-09-31-42.png")