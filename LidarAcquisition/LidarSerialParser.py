# LidarSerialParser

# Packages
import serial
import platform
import pandas as pd

## Main class START
class NewLidarConnection:

#==============================================================================

    def __init__(self, baudrate=115200, timeout=2):
        # Main characteristics of connection
        self.UARTBaudRate = baudrate
        self.UARTTimeout = timeout #s
        # Check for system OS        
        self.myOs = platform.system() # Linux or Windows
        if self.myOs == 'Linux':
            self.UARTSerialPort = '/dev/ttyUSB0' 
        if self.myOs == 'Windows':
            self.UARTSerialPort = 'COM4'
        else:
            raise ("No OS detected!")
        
        self.ConnectToUART()

#==============================================================================
    
    def ConnectToUART(self):
        self.ser = serial.Serial(self.UARTSerialPort, self.UARTBaudRate, timeout=self.UARTTimeout)
        return self.ser.is_open

#==============================================================================

    def GetOneSample(self):    
        line = self.ser.readline()   # read a '\n' terminated line
        theta, distance = line.split(separator=', ')
        return [theta, distance]
## Main class END  

## Main function

lidar0 = NewLidarConnection(baudrate=115200, timeout=3)






with serial.Serial(serialPort, 115200, timeout=5) as ser:
    x = ser.read()          # read one byte
    s = ser.read(10)        # read up to ten bytes (timeout)
    line = ser.readline()   # read a '\n' terminated line

