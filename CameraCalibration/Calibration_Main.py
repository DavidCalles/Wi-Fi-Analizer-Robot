# Main Calibration

#----------------------------------------------------------------------------#
# ------------------------ Add Calibration Module ---------------------------#
#----------------------------------------------------------------------------#
import GenericCalibration as cb

#----------------------------------------------------------------------------#
# -------------------- Calibrate camera with image set ----------------------#
#----------------------------------------------------------------------------#
# Initialize calibration Object
camera0 = cb.NewCalibration(imageSetPath='CalibrationImagesSet',
                            squareSize=27.0,
                            squareGrid=[8,6],
                            imgFormat='jpg',
                            verbose=1)

# Calibrate: 3 iterations over windows over 10 random images
camera0.IterativeCalibration(windowSize=10,
                             iterations=10,
                             showImages=False,
                             showTime=1000,
                             saveImages=False)

# Save calibration in binary file (numpy format)
camera0.ExportCalibrationToFile(savePath='CameraCalibration.npz')