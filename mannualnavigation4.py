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
percentIncrement = 5
distanceUntilCrash = 12
speed = 0.1
dirAngle_Increment = 8
dirAngle_Start = 0
xCamera_Increment = 2
xCamera_Start = 0
yCamera_Increment = 2
yCamera_Start = 0
ultraSensorGuardDistance = 6 #cm
delay = 0.01

#state machine and state times
state = 0
t1 = time.time()
ts = 0
tf = 0.1
tb = 3
#-------------------------- Check for stdin terminal -------------------------#
def isData():
    return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])
    
#-------------------------- Navigation Systen Class- -------------------------#

class navSystem:
    def __init__(self):
        self.myrobot.Picarx()
        

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
    global dirAngle_Start
    global t1
    global state
    global ts
    global tb
    global tf	
    
    while (1):       
        if isData():
            break
        
        #stop state
        if(state == 0):
            myrobot.stop()
            state = 1
        
        #set direction state
        if(state == 1):
            #not near to crash
            if(myrobot.get_distance() > distanceUntilCrash):
                #dandomly deside if the direction angle needs to be adjusted
                if(random.randint(0,2)):
                    # substract from angle if it reached max
                    if(dirAngle_Start > 25):
                        dirAngle_Start = dirAngle_Start - random.randint(0,5)
                        robot_SoftRampForward()
                        t1 = time.time()
                        state = 2
                    # add from angle if it reached min
                    if(dirAngle_Start < -25):
                        dirAngle_Start = dirAngle_Start + random.randint(0,5)
                        robot_SoftRampForward()
                        t1 = time.time()
                        state = 2
                    #add random angle when in between ranges
                    else:
                        dirAngle_Start += random.randint(-5,5)
                        robot_SoftRampForward()
                        t1 = time.time()
                        state = 2
                #no angle change 
                else:
                    dirAngle_Start = dirAngle_Start
                    robot_SoftRampForward()
                    t1 = time.time()
                    state = 2
            #if near crash oposite lock
            else:
                dirAngle_Start = -1 * dirAngle_Start
                robot_SoftRampBackward()
                t1 = time.time()
                state = 3
        
        #ForwardState
        if(state == 2):
            if(myrobot.get_distance() < distanceUntilCrash):
                state = 0
            if(time.time() - t1 < tf):
                robot_SoftRampForward()
                state = 2
            if(time.time() - t1 > tf):
                state = 0
        
         #BorwardState
        if(state == 3):
            if(time.time() - t1 < tb):
                robot_SoftRampForward()
                state = 3
            if(time.time() - t1 > tb):
                state = 0		

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

    myrobot.set_power(0.1) 
    
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
    except:
        myrobot.stop()
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        myrobot.stop()
