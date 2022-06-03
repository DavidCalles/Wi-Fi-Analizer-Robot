# -*- coding: utf-8 -*-

#----------------------------------------------------------------------------#
# ----------------------- REQUIRED EXTERNAL PACKAGES ------------------------#
#----------------------------------------------------------------------------#

import numpy as np
import cv2
import glob
import random 

#----------------------------------------------------------------------------#
# ----------------------- MAIN CALIBRATION OBJECT ---------------------------#
#----------------------------------------------------------------------------#

class NewCalibration:
    
#=============================================================================================== 

    def __init__(self, imageSetPath, squareSize, squareGrid, imgFormat='jpg', verbose=0):
        """Initialize calibration object

        Args:
            imageSetPath (string):  Path to set of calibration images
            squareSize (float):     SizeOf a square in mm
            squareGrid (list):      Square grid (number of corners) 
        """
        self.generalPath = imageSetPath + '/*.' + imgFormat
        self.squareSize = squareSize
        self.squareGrid = squareGrid
        self.verbose = verbose
    
        # Other general variables
        self.show_size = (1080,720)
        self.summary_size = (1800, 500)
        self.allImagesPath = glob.glob(self.generalPath)
        
        # Paths of images
        self.test_path = random.choice(self.allImagesPath) #Single image for testing
        self.save_path = imageSetPath + '_Results/'  #Directory for saving borders imgs
        self.name_num = len(imageSetPath + '/') #Len unitl image name
        
        # termination criteria
        self.criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        
        # assuming z=0 in all cases
        self.objp = np.zeros((squareGrid[0]*squareGrid[1],3), np.float32)
        self.objp[:,:2] = np.mgrid[0:squareGrid[0],0:squareGrid[1]].T.reshape(-1,2)
        self.objp *= squareSize

#===============================================================================================

    def Image_Correction (self, img):
        # GET shape of image
        shape = (img.shape[1]+1, img.shape[0]+1)
        # LOAD intrinsic camera matrix and distortion coefficients vector if it doesnt exist.
        if not hasattr(self, 'Calib_mtx'):
            file=np.load('CameraCalibration.npz')
            self.Calib_mtx, self.Calib_dist, _, _, _, _ = [file[i] for i in (
                'mtx','dist','rvecs','tvecs', 'newcameramtx', 'mean_error')]
        # ESTIMATE new camera matrix
        newcameramtx, roi = cv2.getOptimalNewCameraMatrix(
            cameraMatrix = self.Calib_mtx,
            distCoeffs = self.Calib_dist,
            imageSize = shape,
            alpha = 0,
            newImgSize = shape
        )
        
        # UNDISTORT image
        out_img = np.zeros(img.shape,np.uint8)
        cv2.undistort(
            src = img,
            cameraMatrix = self.Calib_mtx,
            distCoeffs = self.Calib_dist,
            dst = out_img,
            newCameraMatrix = newcameramtx
        )
        # CROP image to ROI
        x,y,w,h = roi
        crop_img = out_img[y : y+h, x : x+w]
        return crop_img

#===============================================================================================
        
    def IterativeCalibration(self, windowSize, iterations,
                             showImages=True, showTime=2000, saveImages=False):
        """_summary_

        Args:
            windowSize (int):       Number of images to use in a single calibration
            iterations (int):       Attempts to calibrate (looking for best set of images)
        """
        self.windowSize = windowSize
        self.iterations = iterations

        # Important values to be found
        error_vect = []
        used_images = []
        matrixes = []
        new_matrixes = []
        distortions = []
        rotations = []
        translations = []
        
        for k in range(iterations):
            print("Initiating attempt {}.".format(k))
            # INITIALIZE values
            objpoints = [] # 3d point in real world space
            imgpoints = [] # 2d points in image plane.
            random_images = random.sample(self.allImagesPath, self.windowSize)
            iteration = 0
            cv2.startWindowThread()
            succesfull = []
            failed = []
            success_count = 0
            
        #----------------------------------------------------------------------------#
        # ---------------- PERFORM EACH ITERATION OF CALIBRATION---------------------#
        #----------------------------------------------------------------------------#
            for fname in random_images:
                iteration += 1
                img = cv2.imread(fname)
                gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
            
                # FIND the chess board corners
                ret, corners = cv2.findChessboardCorners(gray,
                                                        (self.squareGrid[0],self.squareGrid[1]),
                                                        None)

                # ADD object and image points if conerners were detected.
                if ret == True:
                    objpoints.append(self.objp)
                    # REFINE corners coordinates
                    corners2 = cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),
                                                self.criteria)
                    if self.verbose > 1:
                        print(f"Img: {fname[self.name_num:]}, {corners2.shape[0]} corners found")
                    imgpoints.append(corners2)
            
                    # DRAW and DISPLAY the corners
                    if showImages:
                        imgBorders = cv2.drawChessboardCorners(img,
                            (self.squareGrid[0],self.squareGrid[1]), corners2,ret)
                        img_show = cv2.resize(imgBorders, self.show_size)
                        cv2.imshow(fname[self.name_num:], img_show)
                        cv2.waitKey(showTime)
                        cv2.destroyAllWindows()
                    
                    # SAVE image with corners (if enabled)
                    if saveImages:
                        filename = self.save_path + fname[self.name_num:]
                        cv2.imwrite(filename, img)
                        
                    succesfull.append(fname[self.name_num:])
                    success_count = success_count +1
                else:
                    failed.append(fname[self.name_num:])
            
            
            cv2.destroyAllWindows()
            
            # ESTIMATE camera parameters
            ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints,
                                                            imgpoints,
                                                            gray.shape[::-1],
                                                            None,None)
            # LOAD test image
            img = cv2.imread(self.test_path)
            h,  w = img.shape[:2]
            
            # ESTIMATE new optimal camera matrix
            newcameramtx, roi = cv2.getOptimalNewCameraMatrix(cameraMatrix=mtx,
                                                            distCoeffs=dist,
                                                            imageSize=(w,h),
                                                            alpha=1,
                                                            newImgSize=(w,h))
            # UNDISTORT test image
            out_img = img.copy()
            cv2.undistort(src=img, cameraMatrix=mtx, distCoeffs=dist,
                        dst=out_img, newCameraMatrix=newcameramtx)
            
            # CROP ROI of image
            x,y,w,h = roi
            crop_img = out_img[y:y+h, x:x+w]
            
            # RESIZE image
            h,  w = img.shape[:2]
            crop_img_2 = cv2.resize(crop_img, dsize=(w, h),
                                    interpolation=cv2.INTER_LINEAR)
            
            # SHOW undistorting results
            bigImg = cv2.resize(np.hstack([img, out_img, crop_img_2]), self.summary_size)
            if showImages:
                cv2.startWindowThread()
                cv2.namedWindow('Undistorting results', flags =   cv2.WINDOW_NORMAL |
                                cv2.WINDOW_FREERATIO)
                cv2.imshow('Undistorting results', bigImg)
                cv2.waitKey(showTime*3)
                cv2.destroyAllWindows()
            
            # CALCULATE reprojection error of single attempt
            mean_error = 0
            for i in range(len(objpoints)):
                imgpoints2, _ = cv2.projectPoints(objpoints[i], rvecs[i],
                                                tvecs[i], mtx, dist)
                error = cv2.norm(imgpoints[i],imgpoints2, cv2.NORM_L2)/len(imgpoints2)
                mean_error += error

            if self.verbose > 0:
                print(f"In attempt {k}, {success_count} images were proccessed.\n")
                
            # ACCUMULATE all values from each attempt
            error_vect.append(mean_error/len(objpoints))
            used_images.append(succesfull)
            matrixes.append(mtx)
            new_matrixes.append(newcameramtx)
            distortions.append(dist)
            rotations.append(rvecs)
            translations.append(tvecs)

        # SEARCH attempt with most and least error
        maximum_error = np.amax(error_vect)
        minimum_error = np.amin(error_vect)
        location_max = np.argmax(error_vect)
        location_min = np.argmin(error_vect)
        # CALCULATE mean error
        mean_error = np.mean(error_vect)

        # VERBOSE results
        if self.verbose > 0:
            print( "MAXIMUM ERROR FOUND: {} IN ITERATION {}." \
                .format(maximum_error, location_max) )
            print( "MINIMUM ERROR FOUND: {} IN ITERATION {}." \
                .format(minimum_error, location_min) )
            print( "MEAN ERROR FOUND: {} WITH WINDOWS OF {}" \
                .format(mean_error, windowSize) )
            print( "IMAGES TO BE USED: \n", used_images[location_min])
            print( "CAMERA MATRIX TO BE USED: \n", matrixes[location_min])
            print( "DISTORTION VECTOR TO BE USED: \n", distortions[location_min])
        
        # Save results locally
        self.Calib_mtx = matrixes[location_min]
        self.Calib_dist = distortions[location_min]
        self.Calib_rvecs = rotations[location_min]
        self.Calib_tvecs = translations[location_min]
        self.Calib_newcameramtx = new_matrixes[location_min]
        self.Calib_mean_error = minimum_error

#===============================================================================================
        
    def ExportCalibrationToFile(self, savePath='CameraCalibration.npz'):
        # SAVE results to file
        np.savez(savePath, 
            mtx=self.Calib_mtx,
            dist=self.Calib_dist,
            rvecs=self.Calib_rvecs,
            tvecs=self.Calib_tvecs,
            newcameramtx=self.Calib_newcameramtx,
            mean_error=self.Calib_mean_error)
        if self.verbose > 0:
            print(f"Files succesfully saved in {savePath}\n")