# importing sys
import sys
# adding picar-x classes to the system path
sys.path.insert(0, 'RobotSource/picar-x/')
from picarx import *
import time

# Create robot object
myrobot = Picarx()

# Move motors breefly
myrobot.forward(50)
time.sleep(1)
myrobot.stop()

# Get  ultrasonic sensor data
for i in range(10):
    print(myrobot.get_distance())
    time.sleep(1)