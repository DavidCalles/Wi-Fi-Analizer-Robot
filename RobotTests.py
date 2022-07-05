# importing sys
from re import T
import sys
# adding picar-x classes to the system path
sys.path.insert(0, 'RobotSource/picar-x/')
from picarx import *
import time
import keyboard

# Create robot object
myrobot = Picarx()

# Move motors breefly
# myrobot.forward(50)
# time.sleep(1)
# myrobot.stop()
# myrobot.backward(50)
# time.sleep(1)
# myrobot.stop()

# # Get  ultrasonic sensor data
# for i in range(10):
#     print(myrobot.get_distance())
#     time.sleep(1)
# myrobot.stop()
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

motorDelay = 0.3
speed = 10
currentDirAngle = 0
angleLeftIncrement = 5
angleRightIncrement = -5

while True:

    try:      
        if keyboard.is_pressed('q'):
            myrobot.stop()
    
        if keyboard.is_pressed('w'):
            myrobot.forward(speed)
           
        elif keyboard.is_pressed('s'):
            myrobot.backward(speed)

        elif keyboard.is_pressed('a'):
            currentDirAngle += angleLeftIncrement
            myrobot.set_dir_servo_angle(currentDirAngle)     

        elif keyboard.is_pressed('d'):
            currentDirAngle += angleRightIncrement
            myrobot.set_dir_servo_angle(currentDirAngle)
        
        time.sleep(motorDelay)
        myrobot.stop()

        
    
    except:
        myrobot.stop()
        break

