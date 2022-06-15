
#==============================================================================
#-------------------------  Imported Modules   --------------------------------
#==============================================================================

from tabnanny import verbose
from RpiUltrasonic import *

#==============================================================================
#-------------------------   Local Variables   --------------------------------
#==============================================================================

# Set GPIO Pins for this test
triggerPin = 27
echoPin = 17

#==============================================================================
#---------------------------   Main Code   -----------------------------------
#==============================================================================

# Check if platform is ARM (summary for "rpi")
if "arm" in os.uname()[4]:

    try:
        # New sensor object
        sensor0 = UltrasonicSensor(trigger_pin=triggerPin, echo_pin=echoPin, theme='seaborn')
        
        # Save calibration to CSV file 
        sensor0.ImportCalibrationFromFile(path='CalibrationCoeffs.csv')
        
        # Retrieve x number of samples, doing a simple range validation
        # Press key to cancel early
        sensor0.GetDistanceNumSamples(period=0.1, numSamples=100, validRange=[0.1, 150], verbose=False, cancelKey='q')
        sensor0.PlotSamples()
        # Get Dataframe
        print(sensor0.samplesDf.head())
        sensor0.WriteSamplesToJson(path='FormattedSamples.json')

        # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Manual stop")

    # GPIO Cleanup
    sensor0.CloseGPIO()

else:
    print("CARE! Not running in raspberry-pi!!")