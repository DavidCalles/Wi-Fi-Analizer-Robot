
#==============================================================================
#-------------------------  Imported Modules   --------------------------------
#==============================================================================

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
        
        # Calibrate sensor (1 sec wait after entering distance)
        sensor0.CalibrateSemiAutomatic(waitTime=1)
        # Save calibration to CSV file 
        sensor0.ExportCalibrationToFile(path='CalibrationCoeffs.csv')
        
        # Retrieve x number of samples, doing a simple range validation
        sensor0.GetDistanceSamples(period=0.1, numSamples=50, validRange=[0.1, 150])
        print(sensor0.samplesDf)
        sensor0.PlotSamples()

        # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Manual stop")

    # GPIO Cleanup
    sensor0.CloseGPIO()

else:
    print("CARE! Not running in raspberry-pi!!")