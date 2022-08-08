import sys
import time
import select
import tty
import termios
import random

sys.path.append('RobotSource/picar-x/')
from picarx import *

#-------------------------- Check for stdin terminal -------------------------#
def isData():
    return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])
    
#-------------------------- Navigation Systen Class- -------------------------#

class navSystem:
#---------------------------Navigation Initialization ------------------------#
    def __init__(self, xCamera_Increment=2, yCamera_Increment=2, ts=0, tf=0.1, tb=3, 
        dirAngle_Increment = 8, percentIncrement = 5, distanceUntilCrash = 6, 
        speed = 0.1, delay = 0.01, maxAngleAllowed = 35, maxAngleChange = 15, minAngleChange = 6):

        self.myrobot = myrobot.Picarx()

#--------------------------State Machine Variables ---------------------------#
        self.curretnState = 0
        self.initalTime = time.time()
        self.stopTime = ts
        self.forwardTime = tf
        self.backwardTime = tb          
#-----------------------------Angle Variables --------------------------------#   
        self.currentAngle = 0
        self.incrementAngle = dirAngle_Increment
        self.maxAngleA = maxAngleAllowed
        self.maxAngleC = maxAngleChange
        self.minAngleC = minAngleChange
#-----------------------------Ultrasound Variables ----------------------------#
        self.usDistance = distanceUntilCrash
#-----------------------------Manual mode Variables ---------------------------#
        self.speed = speed
        self.manualDistance = distanceUntilCrash
        self.percentInc = percentIncrement
        self.delay = delay
        self.camPosX = 0
        self.camPosY = 0
        self.camIncX = xCamera_Increment
        self.camIncY = yCamera_Increment

        self.speedIncrement = percentIncrement

    
#------------------------------------------- Forward/Backward ----------------#  
    def robot_SoftRampForward(self):
        for i in range(1,self.speedIncrement+1):
            if(self.myrobot.get_distance() > self.manualDistance):
                self.myrobot.forward(i*self.speed/self.speedIncrement)
                time.sleep(self.delay)
            
    def robot_SoftForward(self):
        if(self.myrobot.get_distance() > self.manualDistance):
            self.myrobot.forward(self.speed)
        
    def robot_SoftBackward(self):
        self.myrobot.backward(self.speed)

    def robot_SoftRampBackward(self):
        for i in range(1,self.percentInc+1):
            self.myrobot.backward(i*self.speed/self.percentInc)
            time.sleep(self.delay)
    #--------------------------------------------- Steering ----------------------#
    def robot_SoftSteerRight(self):            
        self.currentAngle += self.incrementAngle
        self.myrobot.set_dir_servo_angle(self.currentAngle)
        
    def robot_SoftSteerLeft(self):            
        self.currentAngle -= self.incrementAngle
        self.myrobot.set_dir_servo_angle(self.currentAngle) 
    #------------------------------------------ Camera Horizontal ----------------#
    def robot_SoftLookLeft(self):            
        self.camPosX -= self.camIncX
        self.myrobot.set_camera_servo1_angle(self.camPosXt)
        
    def robot_SoftLookRight(self):            
        self.camPosX += self.camIncX
        self.myrobot.set_camera_servo1_angle(self.camPosX)
    #------------------------------------------ Camera Vertical ------------------#
    def robot_SoftLookUp(self):           
        self.camPosY += self.camIncY
        self.myrobot.set_camera_servo2_angle(self.camPosY)
        
    def robot_SoftSteerDown(self):           
        self.camPosY -= self.camIncY
        self.myrobot.set_camera_servo2_angle(self.camPosY)    
       
#-------------------------- Movement Funtions --------------------------------#
    def automatic(self):
        while (1):       
            if isData():
                break
            
            #stop state
            if(self.curretnState == 0):
                self.myrobot.stop()
                self.curretnState = 1
            
            #set direction state
            elif(self.curretnState == 1):
                #not near to crash
                if(self.myrobot.get_distance() > self.usDistance):
                    #dandomly deside if the direction angle needs to be adjusted
                    if(random.randint(0,3)):
                        # substract from angle if it reached max
                        if(self.currentAngle > self.maxAngleA):
                            self.currentAngle = self.currentAngle - random.randint(self.minAngleC,self.maxAngleC)                            
                        # add from angle if it reached min
                        elif(self.currentAngle < -self.maxAngleA):
                            self.currentAngle = self.currentAngle + random.randint(self.minAngleC,self.maxAngleC)
                        #add random angle when in between ranges
                        else:
                            self.currentAngle += random.randint(-self.minAngleC,self.maxAngleC)
                    
                    self.myrobot.set_dir_servo_angle(self.currentAngle) 
                    self.robot_SoftRampForward()
                    self.initalTime = time.time()
                    self.curretnState = 2
                    #no angle change                    
                #if near crash oposite lock
                else:
                    self.currentAngle = -self.currentAngle
                    self.myrobot.set_dir_servo_angle(self.currentAngle) 
                    self.robot_SoftRampBackward()
                    self.initalTime = time.time()
                    self.curretnState = 3
            
            #ForwardState
            elif(self.curretnState == 2):
                if(self.myrobot.get_distance() < self.usDistance):
                    self.curretnState = 0
                elif(time.time() - self.initalTime < self.forwardTime):
                    self.curretnState = 2
                elif(time.time() - self.initalTime >= self.forwardTime):
                    self.curretnState = 0
            
            #BackardState
            if(self.curretnState == 3):
                if(time.time() - self.initalTime < self.backwardTime):
                    self.curretnState = 3
                if(time.time() - self.initalTime >= self.backwardTime):
                    self.currentAngle = 0
                    self.myrobot.set_dir_servo_angle(self.currentAngle) 
                    self.curretnState = 0
                    

    def fullNavigation(self):
        self.commands = [['w', self.robot_SoftForward],   
            ['a', self.robot_SoftSteerLeft],
            ['s', self.robot_SoftBackward],
            ['d', self.robot_SoftSteerRight],
            ['q', self.robot_SoftLookLeft],
            ['e', self.robot_SoftLookRight],
            ['r', self.robot_SoftLookUp],
            ['f', self.robot_SoftSteerDown],
		    ['g', self.automatic]]

        self.myrobot.set_power(0.1) 
        
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
                    for cmd in self.commands:
                        if c == cmd[0]:
                            cmd[1]()
                            time.sleep(self.delay)
                    
                    # EXIT MANUAL CONTROL    
                    if c == '\x1b':  # x1b is ESCw
                        break
                
                else:
                    # STOP VEHICLE
                    self.myrobot.stop()
        except:
            self.myrobot.stop()
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
            self.myrobot.stop()

if __name__ == '__main__':
    nav0 = navSystem()
    nav0.fullNavigation()