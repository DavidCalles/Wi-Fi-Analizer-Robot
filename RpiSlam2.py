"""

This file as been modified extensively to implement SLAM in RPself.lidar.
It can run well on Raspberry Pi 3B or 4

Many concepts are taken from rpslam.py : BreezySLAM in Python with SLAMTECH RP A1 self.lidar
https://github.com/simondlevy/BreezySLAM

Consume lidar measurement file and create an image for display.

Adafruit invests time and resources providing this open source code.
Please support Adafruit and open source hardware by purchasing
products from Adafruit!

Written by Dave Astels for Adafruit Industries
Copyright (c) 2019 Adafruit Industries
Licensed under the MIT license.

All text above must be included in any redistribution.
"""

import os
import time
from math import cos, sin, pi, floor
# import pygame
from adafruit_rplidar import RPLidar, RPLidarException
import numpy as np
import matplotlib.pyplot as plt
import paho.mqtt.client as mqtt
from threading import Thread



from breezyslam.algorithms import RMHC_SLAM
from breezyslam.sensors import RPLidarA1 as LaserModel
# from rpself.lidar import RPself.lidar as self.lidar
# from adafruit_rpself.lidar import RPself.lidar as self.lidar
#from roboviz import MapVisualizer


class SlamCompute:
    
    def __init__(self):  
        # Screen width & height
        self.W = 640
        self.H = 480
        self.MAP_SIZE_PIXELS = 250
        self.MAP_SIZE_METERS = 15
        self.MIN_SAMPLES   = 150
        self.SCAN_BYTE = b'\x20'
        self.SCAN_TYPE = 129
        self.slamData = []
        # Setup the RPself.lidar
        self.PORT_NAME = '/dev/ttyUSB0'
        self.lidar = RPLidar(None, self.PORT_NAME)
        # Create an RMHC SLAM object with a laser model and optional robot model
        self.slam = RMHC_SLAM(LaserModel(), self.MAP_SIZE_PIXELS, self.MAP_SIZE_METERS)
        # # Set up a SLAM display
        # viz = MapVisualizer(self.MAP_SIZE_PIXELS, self.MAP_SIZE_METERS, 'SLAM', show_trajectory=True)
        # Initialize an empty self.trajectory
        self.trajectory = []
        # To exit self.lidar scan thread gracefully
        self.runThread = True
        # Initialize empty map
        self.mapbytes = bytearray(self.MAP_SIZE_PIXELS * self.MAP_SIZE_PIXELS)
        # used to scale data to fit on the screen
        self.max_distance = 0
        # x, y, theta = 0, 0, 0
        # Pose will be modified in our threaded code
        self.pose = [0, 0, 0]
        # Curent scan data
        self.distances = []
        self.angles = []
        self.quality = []

        self.scan_data = [0]*360

    def _process_scan(self, raw):
        '''Processes input raw data and returns measurment data'''
        new_scan = bool(raw[0] & 0b1)
        inversed_new_scan = bool((raw[0] >> 1) & 0b1)
        quality = raw[0] >> 2
        if new_scan == inversed_new_scan:
            raise RPLidarException('New scan flags mismatch')
        check_bit = raw[1] & 0b1
        if check_bit != 1:
            raise RPLidarException('Check bit not equal to 1')
        angle = ((raw[1] >> 1) + (raw[2] << 7)) / 64.
        distance = (raw[3] + (raw[4] << 8)) / 4.
        return new_scan, quality, angle, distance

    def lidar_measurements(self, max_buf_meas=500):
        
            self.lidar.set_pwm(800)
            status, error_code = self.health
            
            cmd = self.SCAN_BYTE
            self._send_cmd(cmd)
            dsize, is_single, dtype = self._read_descriptor()
            if dsize != 5:
                raise RPLidarException('Wrong info reply length')
            if is_single:
                raise RPLidarException('Not a multiple response mode')
            if dtype != self.SCAN_TYPE:
                raise RPLidarException('Wrong response data type')
            while True:
                raw = self._read_response(dsize)
                self.log_bytes('debug', 'Received scan response: ', raw)
                if max_buf_meas:
                    data_in_buf = self._serial_port.in_waiting
                    if data_in_buf > max_buf_meas*dsize:
                        self.log('warning',
                                'Too many measurments in the input buffer: %d/%d. '
                                'Clearing buffer...' %
                                (data_in_buf//dsize, max_buf_meas))
                        self._serial_port.read(data_in_buf//dsize*dsize)
                yield self._process_scan(raw)


    def lidar_scans(self, max_buf_meas=800, min_len=100):
            
            scan = []
            iterator = self.lidar_measurements(max_buf_meas)
            for new_scan, quality, angle, distance in iterator:
                if new_scan:
                    if len(scan) > min_len:
                        yield scan
                    scan = []
                if quality > 0 and distance > 0:
                    scan.append((quality, angle, distance))


    def slam_compute(self, poseQ, mapbytesQ, rawDataQ):

        try:

            # We will use these to store previous scan in case current scan is inadequate
            previous_distances = None
            previous_angles = None
            scan_count = 0

            for scan in self.lidar_scans():

                # To stop the thread
                if not self.runThread:
                    break

                scan_count += 1

                # Extract (self.quality, angle, distance) triples from current scan
                items = [item for item in scan]

                # Extract self.distances and self.angles from triples
                self.distances = [item[2] for item in items]
                self.angles = [item[1] for item in items]
                self.quality = [item[0] for item in items]
                rawDataQ.put([self.distances, self.angles, self.quality])

                # Update SLAM with current self.lidar scan and scan self.angles if adequate
                if len(self.distances) > self.MIN_SAMPLES:
                    self.slam.update(self.distances, scan_angles_degrees=self.angles)
                    previous_distances = self.distances.copy()
                    previous_angles    = self.angles.copy()

                # If not adequate, use previous
                elif previous_distances is not None:
                    self.slam.update(previous_distances, scan_angles_degrees=previous_angles)

                # Get new position
                self.pose = [0,0,0]
                self.pose[0], self.pose[1], self.pose[2] = self.slam.getpos()
                poseQ.put(self.pose)

                # Get current map bytes as grayscale
                self.slam.getmap(self.mapbytes)
                mapbytesQ.put(self.mapbytes)
                # 
            print("Exiting self.lidar")

        except KeyboardInterrupt:
            self.lidar.stop()
            self.lidar.disconnect()
            raise



# # Launch the self.slam computation thread
# thread = Thread(target=slam_compute,
#                 args=(self.pose, self.mapbytes))
# thread.daemon = True
# thread.start()

# try:
#     # Loop forever,displaying current map and self.pose
#     while True:

#         print("x = " + str(self.pose[0]) + " y = " + str(self.pose[1]) + "theta = " + str(self.pose[2]))
#         # if not viz.display(self.pose[0]/1000., self.pose[1]/1000., self.pose[2], self.mapbytes):
#         #     raise KeyboardInterrupt


# except KeyboardInterrupt:
#     self.runThread = False
#     thread.join()
#     self.lidar.stop()
#     self.lidar.disconnect()
#     exit(0)