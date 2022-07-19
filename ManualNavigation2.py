import sys
import time
import select
import tty
import termios

sys.path.append('RobotSource/picar-x/')
from picarx import *

#-------------------------- Robot Parameters -------------------------#
myrobot = Picarx()
speed = 50
steerIncrement = 5
initialAngle = 0

#-------------------------- Check for stdin terminal -------------------------#
def isData():
    return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])

#-------------------------- Movement Funtions -------------------------#
def robot_SoftSteerRight():
    global initialAngle
    initialAngle += steerIncrement
    myrobot.set_dir_servo_angle(initialAngle)
    
def robot_SoftSteerLeft():
    global initialAngle
    initialAngle -= steerIncrement
    myrobot.set_dir_servo_angle(initialAngle)
    
def robot_SoftForward():
    myrobot.forward(speed)
    
def robot_SoftBackward():
    myrobot.backward(speed)

commands = [['w', robot_SoftForward],
            ['a', robot_SoftSteerLeft],
            ['s', robot_SoftBackward],
            ['d', robot_SoftSteerRight]]
            
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
                if c == 'f':
                    print("OMG lol4")
                      
                # BASIC MANUAL CONTROL
                for cmd in commands:
                    if c == cmd[0]:
                        cmd[1]()
                        time.sleep(0.01)
                
                # EXIT MANUAL CONTROL    
                if c == '\x1b':  # x1b is ESCw
                    break
            
            else:
                # STOP VEHICLE
                myrobot.stop()

    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)