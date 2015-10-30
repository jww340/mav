# .. -*- coding: utf-8 -*-
#
# ************************************
# camera_calib.py - Calibrate a camera
# ************************************
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
        self.cameraCalib = CameraCalibChessboard(9, 6)
        self.grab = False

    def _processImage(self,
      # The OpenCV image to process.
      cvImage):

        if self.grab:
            self.grab = False
            calibImage, calibError, reprojectionError = \
              self.cameraCalib.processFrame(cvImage)
            cvImageToQt(calibImage, self.lCalib)
            if calibError is not False:
                self.statusBar().showMessage('Calibration error is {}. '
                  'Reprojection error is {}'.format(calibError,
                                                    reprojectionError))
            else:
                self.statusBar().showMessage('Failed')

        if self.cbUndistorted.isChecked():
            cvImageToQt(self.cameraCalib.undistort(cvImage), self.lOrig)
        else:
            cvImageToQt(cvImage, self.lOrig)

    @pyqtSlot()
    def on_pbRestartCalib_clicked(self):
        self.cameraCalib = CameraCalibChessboard(9, 6)
        self.pbGrab.setEnabled(True)

    @pyqtSlot()
    def on_pbGrab_clicked(self):
        self.grab = True


# Adapted from http://docs.opencv.org/master/dc/dbb/tutorial_py_calibration.html.
class CameraCalibChessboard(object):
    def __init__(self,
      # Chessboard pattern size rows. See ``patternSize`` in `findChessboardCorners <http://docs.opencv.org/modules/calib3d/doc/camera_calibration_and_3d_reconstruction.html#findchessboardcorners>`_.
      # For example:
      #
      # .. figure:: chessboard_pattern.png
      #    :width: 200
      #
      #    This chessboard's ``patternSize`` is 9x6.
      patternSizeRows,
      # Chessboard pattern size columns. See above.
      patternSizeColumns):

        self.patternSize = (patternSizeRows, patternSizeColumns)

        # Termination criteria for cornerSubPix.
        self.criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30,
                         0.001)

        # Prepare object points, like (0,0,0), (1,0,0), (2,0,0) ..., (6,5,0)
        self.objp = np.zeros((patternSizeRows*patternSizeColumns, 3),
                             np.float32)
        self.objp[:, :2] = np.mgrid[0:patternSizeRows,
                                    0:patternSizeColumns].T.reshape(-1, 2)

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
    def processFrame(self, cvImage):
        gray = cv2.cvtColor(cvImage, cv2.COLOR_BGR2GRAY)

        # Search for chessboard corners. See findChessboardCorners_.
        found, corners = cv2.findChessboardCorners(gray, self.patternSize)

        # Draw and display the corners. See http://docs.opencv.org/modules/calib3d/doc/camera_calibration_and_3d_reconstruction.html#drawchessboardcorners.
        calibImage = cvImage.copy()
        cv2.drawChessboardCorners(calibImage, self.patternSize, corners, found)

        if found:
            # Prepare space to record the object points.
            self.objpoints.append(self.objp)

            # Refine, then save the image points. See http://docs.opencv.org/modules/imgproc/doc/feature_detection.html#cornersubpix.
            cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), self.criteria)
            self.imgpoints.append(corners)

            # Run the calibration on data gathered thus far. See http://docs.opencv.org/modules/calib3d/doc/camera_calibration_and_3d_reconstruction.html#calibratecamera.
            err, self.cameraMatrix, self.distortionCoeffs, rvecs, tvecs = \
              cv2.calibrateCamera(self.objpoints, self.imgpoints,
                                  gray.shape[::-1])

            # Compute the reprojection error.
            totalError = 0
            for i in xrange(len(self.objpoints)):
                # See http://docs.opencv.org/2.4/modules/calib3d/doc/camera_calibration_and_3d_reconstruction.html#projectpoints.
                imgpoints2, _ = cv2.projectPoints(self.objpoints[i], rvecs[i],
                  tvecs[i], self.cameraMatrix, self.distortionCoeffs)
                totalError += cv2.norm(self.imgpoints[i], imgpoints2,
                                       cv2.NORM_L2)/len(imgpoints2)
            meanError = totalError/len(self.objpoints)

            return calibImage, err, meanError
        else:
            return calibImage, False, False

    def undistort(self, cvImage):
        # See http://docs.opencv.org/modules/imgproc/doc/geometric_transformations.html#undistort.
        return cv2.undistort(cvImage, self.cameraMatrix, self.distortionCoeffs)
#
# Main
# ====
if __name__ == "__main__":
    main(CalibMainWindow, uiFile='camera_calib.ui')
