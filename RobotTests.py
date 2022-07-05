# importing sys
from re import T
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
myrobot.backward(50)
time.sleep(1)
myrobot.stop()

# # Get  ultrasonic sensor data
# for i in range(10):
#     print(myrobot.get_distance())
#     time.sleep(1)
myrobot.stop()
# while (1):
#     try:
#         distance = myrobot.get_distance()
#         if distance < 15.0:
#             print(distance)
#             myrobot.backward(10)
#             time.sleep(2) 
#         else:
#             myrobot.forward(10)

#     except:
try:
    while True:
        char = screen.getch()

        if char == ord('q'):
            break

        if keyboard.is_pressed('w'): #move forward all 4 motors(11,15,31,35)
           myrobot.forward(10)
            break

        elif char == ord('s') : #move backword all 4 motors(13,16,33,37)
            myrobot.backward(10)
        except:
            myrobot.stop()
