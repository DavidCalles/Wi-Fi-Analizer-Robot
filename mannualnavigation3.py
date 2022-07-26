import sys
import time
import select
import tty
import termios
import random

sys.path.append('RobotSource/picar-x/')
from picarx import *

#-------------------------- Robot Parameters -------------------------#
myrobot = Picarx()
percentIncrement = 10
distanceUntilCrash = 12
speed = 25
dirAngle_Increment = 8
dirAngle_Start = 0
xCamera_Increment = 2
xCamera_Start = 0
yCamera_Increment = 2
yCamera_Start = 0
ultraSensorGuardDistance = 6 #cm
delay = 0.01
#-------------------------- Check for stdin terminal -------------------------#
def isData():
    return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])

#-------------------------- Movement Funtions --------------------------------#
#--------------------------------------------- Steering ----------------------#
def robot_SoftSteerRight():
    global dirAngle_Start
    dirAngle_Start += dirAngle_Increment
    myrobot.set_dir_servo_angle(dirAngle_Start)
    
def robot_SoftSteerLeft():
    global dirAngle_Start
    dirAngle_Start -= dirAngle_Increment
    myrobot.set_dir_servo_angle(dirAngle_Start) 

#------------------------------------------- Forward/Backward ----------------#  
def robot_SoftRampForward():
    for i in range(1,percentIncrement+1):
        if(myrobot.get_distance() > distanceUntilCrash):
            myrobot.forward(i*speed/percentIncrement)
            time.sleep(delay)
          
def robot_SoftForward():
    if(myrobot.get_distance() > distanceUntilCrash):
        myrobot.forward(speed)
    
def robot_SoftBackward():
    myrobot.backward(speed)

def robot_SoftRampBackward():
    for i in range(1,percentIncrement+1):
        myrobot.backward(i*speed/percentIncrement)
        time.sleep(delay)

#------------------------------------------ Camera Horizontal ----------------#
def robot_SoftLookLeft():
    global xCamera_Start
    xCamera_Start -= xCamera_Increment
    myrobot.set_camera_servo1_angle(xCamera_Start)
    
def robot_SoftLookRight():
    global xCamera_Start
    xCamera_Start += xCamera_Increment
    myrobot.set_camera_servo1_angle(xCamera_Start)

#------------------------------------------ Camera Vertical ------------------#
def robot_SoftLookUp():
    global yCamera_Start
    yCamera_Start += yCamera_Increment
    myrobot.set_camera_servo2_angle(yCamera_Start)
    
def robot_SoftSteerDown():
    global yCamera_Start
    yCamera_Start -= yCamera_Increment
    myrobot.set_camera_servo2_angle(yCamera_Start)

#------------------------------------------ Random Mode ----------------------#
def robot_random_mode():
    while (1):
        rcase = random.randint(1,3)
        if isData():
            break
        
        elif(rcase == 1):
            global dirAngle_Start
            myrobot.stop()
            if (abs(dirAngle_Start) < 40):
                dirAngle_Start += random.randint(-7,7)
                myrobot.set_dir_servo_angle(dirAngle_Start)                
            time.sleep(5*delay)
            
        elif(rcase == 2):
            if(myrobot.get_distance() > distanceUntilCrash):
                robot_SoftRampForward()
                time.sleep(delay)
            else:
                robot_SoftRampBackward()
                dirAngle_Start = -dirAngle_Start
                time.sleep(2)

#if there is an obstracle move backware
#make the timme a define constant
# just backwared when there is obstravles 
		

commands = [['w', robot_SoftForward],   
            ['a', robot_SoftSteerLeft],
            ['s', robot_SoftBackward],
            ['d', robot_SoftSteerRight],

            ['q', robot_SoftLookLeft],
            ['e', robot_SoftLookRight],
            ['r', robot_SoftLookUp],
            ['f', robot_SoftSteerDown],
		    ['g', robot_random_mode]]
            
if __name__ == '__main__':

    old_settings = termios.tcgetattr(sys.stdin)
    try:
        tty.setcbreak(sys.stdin.fileno())

        while 1:
            # Look for changes in input
            if isData():
                # Read 1 character
                c = sys.stdin.read(1)
                
                # SAMPLE COMPARISON
                if c == 't':
                    print("OMG lol4")
                      
                # BASIC MANUAL CONTROL
                for cmd in commands:
                    if c == cmd[0]:
                        cmd[1]()
                        time.sleep(delay)
                
                # EXIT MANUAL CONTROL    
                if c == '\x1b':  # x1b is ESCw
                    break
            
            else:
                # STOP VEHICLE
                myrobot.stop()

    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)