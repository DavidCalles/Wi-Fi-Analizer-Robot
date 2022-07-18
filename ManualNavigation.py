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

motorDelay = 0.3
speed = 10
currentDirAngle = 0
angleLeftIncrement = 5
angleRightIncrement = -5
angle1upIncrement = 5
angle1downIncrement = -5
angle2upIncrement = 5
angle2downIncrement = 5

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
         
        elif keyboard.is_pressed('1'):
            myrobot.self.set_motor_speed(1, speed)
            
        elif keyboard.is_pressed('2'):
            myrobot.self.set_motor_speed(2, speed)
            
        elif keyboard.is_pressed('3'):
            currentDirAngle += angle1upIncrement
            myrobot.self.camera_servo_pin1.angle(currentDirAngle)
            
        elif keyboard.is_pressed('4'):
            currentDirAngle += angle1downIncrement
            myrobot.self.camera_servo_pin1.angle(currentDirAngle)
            
        elif keyboard.is_pressed('5'):
            currentDirAngle += angle2upIncrement
            myrobot.self.camera_servo_pin2.angle(currentDirAngle)
            
        elif keyboard.is_pressed('6'):
            currentDirAngle += angle2downIncrement
            myrobot.self.camera_servo_pin2.angle(currentDirAngle)
            
        elif keyboard.is_pressed('7'):
            currentDirAngle += angleLeftIncrement
            myrobot.self.dir_servo_pin.angle(currentDirAngle)
            
        elif keyboard.is_pressed('8'):
            currentDirAngle += angleRightIncrement
            myrobot.self.dir_servo_pin.angle(currentDirAngle)
            
        elif keyboard.is_pressed('0'):
            currentDirAngle += angleLeftIncrement
            myrobot.self.dir_servo_pin.angle(0)
            myrobot.self.camera_servo_pin1.angle(0)
            myrobot.self.camera_servo_pin2.angle(currentDirAngle)
        
        time.sleep(motorDelay)
        myrobot.stop()
       
    except:
        myrobot.stop()
        break

