#==============================================================================
#-------------------------  Imported Modules   --------------------------------
#==============================================================================

import RPi.GPIO as GPIO
import time
import pandas as pd
import plotly.express as px
import numpy as np
from scipy import optimize

import os
 
#==============================================================================
#---------------------------   Main Class   -----------------------------------
#==============================================================================

class UltrasonicSensor:

#-------------------------   Init Method   ------------------------------------

    def __init__(self, trigger_pin, echo_pin):

        self.trigger_pin = trigger_pin
        self.echo_pin = echo_pin
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

    def GetDistanceSamples(self, period, numSamples):
        
        #Initialize empty array for data
        self.samples = []

        #Retrieve raw data points
        for i in range(numSamples):
            self.samples.append(self.GetDistanceBlocking())
            time.sleep(period)

        self.samplesDf = pd.DataFrame(data=self.samples, columns=['TimeStamp', 'Distance'])

#==============================================================================

    def WriteSamplesToJson(self, path):

        #Write to JSON file
        self.samplesDf.to_json(path, orient='records')

#==============================================================================

    def CalibrateManual(self, expectedPoints, realPoints):
        pass

#==============================================================================

    def CalibrateSemiAutomatic(self):
        pass

#==============================================================================

    def PlotRawSamples(self, theme='plotly_dark'):

        if hasattr(self, 'samplesDf'):
            fig = px.line(self.samplesDf, x='TimeStamp', y='Distance',
                color='Distance', template=theme)
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
if os.uname()[4].startsWith("arm"):

    try:
        # New sensor object
        sensor0 = UltrasonicSensor(triggerPin, echoPin)
        # Retrieve x number of samples
        sensor0.GetDistanceSamples(period=0.1, numSamples=50)
        sensor0.PlotRawSamples()

        # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Manual stop")

    # GPIO Cleanup
    sensor0.CloseGPIO()

else:
    print("CARE! Not running in raspberry-pi!!")