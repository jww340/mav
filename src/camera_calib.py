# .. -*- coding: utf-8 -*-
#
# **********************************************************
# cv_video.py - Image processing using a webcam with OpenCV.
# **********************************************************
# Imports
# =======
# Library imports
# ---------------
# None.
#
# Third-party imports
# -------------------
import cv2
import numpy as np

# Set the Pyqt API before importing it.
import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)
from PyQt4.QtCore import pyqtSlot
#
# Local imports
# -------------
from cv_video import MainWindow, main, cvImageToQt
#
# Main window
# ===========
class CalibMainWindow(MainWindow):
    def __init__(self, *args, **kwargs):
        super(CalibMainWindow, self).__init__(*args, **kwargs)
        self.cameraCalib = CameraCalibChessboard()
        self.grab = False

    def _processImage(self,
      # The OpenCV image to process.
      cvImage):

        cvImageToQt(cvImage, self.lOrig)
        if self.grab:
            self.grab = False
            calibImage, undistortImage, err = self.cameraCalib.processFrame(cvImage)
            if calibImage is not None:
                cvImageToQt(calibImage, self.lCalib)
                self.statusBar().showMessage('Error is {}'.format(err))
            else:
                self.statusBar().showMessage('Failed')

    @pyqtSlot()
    def on_pbRestartCalib_clicked(self):
        self.cameraCalib = CameraCalibChessboard()
        self.pbGrab.setEnabled(True)

    @pyqtSlot()
    def on_pbGrab_clicked(self):
        self.grab = True


# Taken from http://docs.opencv.org/master/dc/dbb/tutorial_py_calibration.html.
class CameraCalibChessboard(object):
    def __init__(self):
        # termination criteria
        self.criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30,
                         0.001)

        # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ..., (6,5,0)
        self.objp = np.zeros((9*6, 3), np.float32)
        self.objp[:, :2] = np.mgrid[0:9, 0:6].T.reshape(-1, 2)

        # Initial camera matrix and (non)distortion coefficients.
        self.cameraMatrix = np.eye(3, dtype=np.float64)
        self.distortionCoeffs = np.zeros((8, 1), np.float64)

        # Arrays to store object points and image points from all the images.
        #
        # 3d point in real world space
        self.objpoints = []
        # 2d points in image plane.
        self.imgpoints = []

    # Search for the chessboard in this frame, updating the camera calibration
    # if it was found.
    def processFrame(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Search for chessboard corners.
        found, corners = cv2.findChessboardCorners(gray, (9, 6), None)

        # Draw and display the corners.
        calibImage = image.copy()
        cv2.drawChessboardCorners(calibImage, (9, 6), corners, found)

        if found:
            # Prepare space to record the object points.
            self.objpoints.append(self.objp)

            # Refine, then save the image points.
            cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), self.criteria)
            self.imgpoints.append(corners)

            # Run the calibration on data gathered thus far.
            print(image.shape[::-1])
            err, self.cameraMatrix, self.distortionCoeffs, rvecs, tvecs = cv2.calibrateCamera(self.objpoints,
              self.imgpoints, gray.shape[::-1])
            undistortImage = cv2.undistort(image, self.cameraMatrix,
                                           self.distortionCoeffs, None)

            return calibImage, undistortImage, err
        else:
            return calibImage, None, None
#
# Main
# ====
if __name__ == "__main__":
    main(CalibMainWindow, uiFile='camera_calib.ui')
