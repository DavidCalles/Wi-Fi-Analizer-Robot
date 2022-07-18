from threading import Thread, Timer ,Lock
from picamera import PiCamera
from datetime import datetime
import sys 
import time

projectPath = "/home/davidcalles/Documents/Wi-Fi-Analizer-Robot/"
sys.path.append('CameraCalibration/')

# Camera variables
imgCounter = 0
Task0StopCondition = 1
Task1StopCondition = 1
# camera = PiCamera()

# # Camera task
# def CameraTask():
#     path=projectPath+"CameraCalibration/img_"+str(imgCounter)+".jpg"
#     imgCounter+=1
#     camera.capture(path)

## Locking resources
myLock = Lock()
    
def TestTask0():
    global imgCounter
    global Task0StopCondition
    while(Task0StopCondition):
        myLock.acquire()
        print(f"TaskTest0->{imgCounter}")
        imgCounter+=1
        myLock.release()
        time.sleep(1)
    
def TestTask1():
    global imgCounter
    global Task1StopCondition
    while(Task1StopCondition):
        myLock.acquire()
        print(f"TaskTest1->{imgCounter}")
        imgCounter+=1
        myLock.release()
        time.sleep(2)

t0 = Thread(target=TestTask0, args=[])
t1 = Thread(target=TestTask1, args=[])

t0.start()
t1.start() 

time.sleep(11)
Task0StopCondition = 0
Task1StopCondition = 0
t0.join()
t1.join() 

# Running Tasks
