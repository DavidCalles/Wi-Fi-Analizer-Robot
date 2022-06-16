#==============================================================================
#-------------------------  Imported Modules   --------------------------------
#==============================================================================

import RPi.GPIO as GPIO
import time
import pandas as pd
import plotly.express as px
import numpy as np
import datetime as dt
from datetime import datetime
import plotly.graph_objects as go
import sys
import select

import os
 
#==============================================================================
#---------------------   General Purpose Functions   -------------------------
#==============================================================================

def NonBlocking_IsThereInput():
    return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])

def NonBlocking_InputIsKey(key='q'):
    if NonBlocking_IsThereInput():
        c = sys.stdin.readline().rstrip()
        if c == key:
            return 1
    return 0

def CalibrateSample(sample, coeffs):
    return (coeffs[0]*sample + coeffs[1])

def VerifySample(sample, ranges = [1, 200]):
    if(sample < ranges[1]) and (sample > ranges[0]):
        return sample
    else:
        return -1
 
#==============================================================================
#---------------------------   Main Class   -----------------------------------
#==============================================================================

class UltrasonicSensor:

#-------------------------   Init Method   ------------------------------------

    def __init__(self, trigger_pin=27, echo_pin=17, theme='plotly_dark'):

        self.trigger_pin = trigger_pin
        self.echo_pin = echo_pin
        self.theme = theme
        self.startTime = 0
        self.distance = 0

        #set GPIO Mode (BOARD / BCM)
        GPIO.setmode(GPIO.BCM)  

        #set GPIO direction (IN / OUT)
        GPIO.setup(trigger_pin, GPIO.OUT)
        GPIO.setup(echo_pin, GPIO.IN)

#-----------------------------   Methods   ------------------------------------

    def GetDistanceBlocking(self):
        # set Trigger to HIGH
        GPIO.output(self.trigger_pin, True)
    
        # set Trigger after 0.01ms to LOW
        time.sleep(0.00001)
        GPIO.output(self.trigger_pin, False)
    
        # Wait for rising edge
        while GPIO.input(self.echo_pin) == 0:
            pass
            # Do nothing
        self.startTime = time.time()
    
        # Wait for falling edge
        while GPIO.input(self.echo_pin) == 1:
            pass
        
        # Calculate basic distance 
        self.distance = ((time.time() - self.startTime) * 34300) / 2
    
        return self.startTime, self.distance

#==============================================================================

    def GetDistanceSamples(self, period=0.1, numSamples=50, validRange=[0.1, 150.0], verbose=True, cancelKey='q'):
        
        #Initialize empty array for data
        self.samples = []
        sampleId = 0
        #Retrieve raw data points
        while (sampleId <= numSamples) or (numSamples == -1):
            potentialSample = self.GetDistanceBlocking()
            # Basic data validation
            if((potentialSample[1] >= validRange[0]) and (potentialSample[1] <= validRange[1])):
                self.samples.append(potentialSample.insert(0, sampleId))
                sampleId += 1
                if verbose:
                    print(potentialSample)
                if NonBlocking_InputIsKey(key=cancelKey):
                    break
                time.sleep(period)

        self.samplesDf = pd.DataFrame(data=self.samples, columns=['SampleId', 'Epoch', 'Distance'])
        self.samplesDf['DateTimeUTC'] = self.samplesDf['Epoch'].apply(lambda x: datetime.fromtimestamp(x))

        # If Calibration is found
        if hasattr(self, 'coeffs'):
            self.samplesDf['Calibrated Distance'] = self.samplesDf['Distance'].apply(lambda x: (self.coeffs[0]*x+self.coeffs[1]))
            self.samplesDf = self.samplesDf.astype({"Calibrated Distance": float, "Distance": float}) 

#==============================================================================

    def WriteSamplesToJson(self, path):

        #Write to JSON file
        self.samplesDf.to_json(path, orient='records')

#==============================================================================

    def CalibrateManual(self, df, plot=False):

        x = df.Real.to_numpy(copy=True)
        y = df.Sensed.to_numpy(copy=True)

        # Matrix A
        A = np.vstack([x, np.ones(len(x))]).T
        # Y data into a column vector
        y2 = y[:, np.newaxis]

        # Direct least square regression
        self.coeffs = np.dot((np.dot(np.linalg.inv(np.dot(A.T, A)), A.T)), y2)
        print(f'Equation => y = {self.coeffs[0]}x + {self.coeffs[1]}')

        #Plot results
        if plot:
            y2 = self.coeffs[0]*x + self.coeffs[1]
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=x, y=y,
                                mode='markers', name='Calibration Points'))
            fig.add_trace(go.Scatter(x=x, y=y2,
                                mode='lines', name='Fitted Line'))
            # Edit the layout
            fig.update_layout(title='Calibration Points of Ultrasonic Sensor',
                xaxis_title='Sensed Distance (Cm)',
                yaxis_title='Real Measured Distance (Cm)',
                template=self.theme)
            fig.show()

#==============================================================================

    def CalibrateSemiAutomatic(self, waitTime):
        self.calibrationPoints = []
        # Get first point
        realValue = input("We will take our FIRST point, please measure the distance and insert it here:")
        time.sleep(waitTime)
        _, sensedValue = self.GetDistanceBlocking()
        self.calibrationPoints.append((realValue, sensedValue))

        #Second point
        realValue = input("Now for the SECOND one, please measure the distance and insert it here:")
        time.sleep(waitTime)
        _, sensedValue = self.GetDistanceBlocking()
        self.calibrationPoints.append((realValue, sensedValue))  

        #Third point
        realValue = input("And the THIRD one, please measure the distance and insert it here:")
        time.sleep(waitTime)
        _, sensedValue = self.GetDistanceBlocking()
        self.calibrationPoints.append((realValue, sensedValue)) 

        #As much extra points as the user desires
        while input("Do you wish to add more points? (y/n)") not in ['n', 'N', 'no', 'No']:
            realValue = input("Please measure the distance and insert it here:")
            time.sleep(waitTime)
            _, sensedValue = self.GetDistanceBlocking()
            self.calibrationPoints.append((realValue, sensedValue))
        
        self.calibrationPointsDf = pd.DataFrame(data=self.calibrationPoints, columns=['Real', 'Sensed'], dtype=float)
        print("Calibrating with the following points:")
        print(self.calibrationPointsDf)

        # Calibrate with retrieved points
        self.CalibrateManual(self.calibrationPointsDf)
        
#==============================================================================

    def ExportCalibrationToFile(self, path):
        if hasattr(self, "coeffs"):
            np.savetxt(path, self.coeffs, delimiter=",")
        else:
            raise ValueError("Calibration could not be found")
    
    def ImportCalibrationFromFile(self, path):    
        self.coeffs = np.genfromtxt(path, delimiter=',')
        return self.coeffs  

#==============================================================================

    def PlotSamples(self):

        if hasattr(self, "coeffs"):
            fig = px.line(self.samplesDf, x='DateTimeUTC', y=['Distance', 'Calibrated Distance'], template=self.theme,
            labels={
                     "Formatted TimeStamp": "Time (Date)",
                     "Distance": "Distance (cm)",
                     "Calibrated Distance": "Distance (cm)"
                },
                title="Ultrasonic Sensor Raw and Calibrated Data")    
            fig.show()
        elif hasattr(self, 'samplesDf'):
            fig = px.line(self.samplesDf, x='DateTimeUTC', y='Distance', template=self.theme,
            labels={
                     "Formatted TimeStamp": "Time (Date)",
                     "Distance": "Distance (cm)"
                },
                title="Ultrasonic Sensor Raw Data")
            fig.show()
        else:
            print("There are no points to plot")

#==============================================================================

    def CloseGPIO(self):
        GPIO.cleanup()