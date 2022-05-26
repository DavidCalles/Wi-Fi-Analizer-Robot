#==============================================================================
#-------------------------  Imported Modules   --------------------------------
#==============================================================================

from tkinter import Y
import RPi.GPIO as GPIO
import time
import pandas as pd
import plotly.express as px
import numpy as np
import datetime as dt
import plotly.graph_objects as go

import os
 
#==============================================================================
#---------------------------   Main Class   -----------------------------------
#==============================================================================

class UltrasonicSensor:

#-------------------------   Init Method   ------------------------------------

    def __init__(self, trigger_pin, echo_pin, theme='plotly_dark'):

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

    def GetDistanceSamples(self, period, numSamples, validRange=[0.1, 150.0]):
        
        #Initialize empty array for data
        self.samples = []

        #Retrieve raw data points
        for i in range(numSamples):
            potentialSample = self.GetDistanceBlocking()
            # Basic data validation
            if((potentialSample[1] >= validRange[0]) and (potentialSample[1] <= validRange[1])):
                self.samples.append(potentialSample)
                time.sleep(period)

        self.samplesDf = pd.DataFrame(data=self.samples, columns=['TimeStamp', 'Distance'])
        self.samplesDf['Formatted TimeStamp'] = self.samplesDf['TimeStamp'].apply(lambda x: dt.datetime.fromtimestamp(x))

        # If Calibration is found
        if hasattr(self, 'coeffs'):
            self.samplesDf['Calibrated Distance'] = self.samplesDf['Distance'].apply(lambda x: (self.coeffs[0]*x+self.coeffs[1]))
            self.samplesDf = self.samplesDf.astype({"Calibrated Distance": float, "Distance": float}) 

#==============================================================================

    def WriteSamplesToJson(self, path):

        #Write to JSON file
        self.samplesDf.to_json(path, orient='records')

#==============================================================================

    def CalibrateManual(self, df):

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

    def PlotSamples(self):

        if hasattr(self, "coeffs"):
            fig = px.line(self.samplesDf, x='Formatted TimeStamp', y=['Distance', 'Calibrated Distance'], template=self.theme,
            labels={
                     "Formatted TimeStamp": "Time (Date)",
                     "Distance": "Distance (cm)",
                     "Calibrated Distance": "Distance (cm)"
                },
                title="Ultrasonic Sensor Raw and Calibrated Data")    
            fig.show()
        elif hasattr(self, 'samplesDf'):
            fig = px.line(self.samplesDf, x='Formatted TimeStamp', y='Distance', template=self.theme,
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

#==============================================================================

#==============================================================================
#---------------------------   Main Code   -----------------------------------
#==============================================================================

# Set GPIO Pins for this test
triggerPin = 27
echoPin = 17

# Check if platform is ARM (summary for "rpi")
if "arm" in os.uname()[4]:

    try:
        # New sensor object
        sensor0 = UltrasonicSensor(triggerPin, echoPin, 'seaborn')
        
        # Calibrate sensor (1 sec wait after entering distance)
        sensor0.CalibrateSemiAutomatic(waitTime=1)

        # Retrieve x number of samples, doing a simple range validation
        sensor0.GetDistanceSamples(period=0.1, numSamples=50, validRange=[0.1, 150])
        #print(sensor0.samplesDf)
        sensor0.PlotSamples()

        # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Manual stop")

    # GPIO Cleanup
    sensor0.CloseGPIO()

else:
    print("CARE! Not running in raspberry-pi!!")