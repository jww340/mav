# .. -*- coding: utf-8 -*-
#
# **********************************************************
# cv_video.py - Image processing using a webcam with OpenCV.
# **********************************************************
# Imports
# =======
# Library imports
# ---------------
import sys
from os.path import dirname, join
#
# Third-party imports
# -------------------
import cv2
import numpy as np

# Set the Pyqt API before importing it.
import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)
from PyQt4.QtCore import QTimer, QElapsedTimer, pyqtSlot
from PyQt4.QtGui import QMainWindow, QApplication, QImage, QPixmap, QLabel
from PyQt4 import uic
#
# Helper functions
# ================
def cvImageToQt(
  # The image from OpenCV (as a numpy matrix).
  cvImage,
  # The QLabel to place it in.
  qLabel):

    qi = QImage(cvImage.data, cvImage.shape[1], cvImage.shape[0],
                QImage.Format_RGB888).rgbSwapped()
    qLabel.setFixedHeight(cvImage.shape[0])
    qLabel.setFixedWidth(cvImage.shape[1])
    qLabel.setPixmap(QPixmap.fromImage(qi))
#
# Main window
# ===========
# This class provides a main window which reads from the webcam then processes the resulting image. It should be invoked from within a context manager. When inheriting, simply override ``processImage`` to customize the image processing.
class MainWindow(QMainWindow):
    def __init__(self,
      # Webcam index (0 = first, etc.).
      webcamIndex=0,
      # Resolution, as an index into ``self.supported_resolution``.
      webcamInitialResolution=-1,
      # Qt Designer file to load.
      uiFile=None,
      # Other args to pass on to Qt.
      *args, **kwargs):

        super(MainWindow, self).__init__(*args, **kwargs)
        self.uiFile = uiFile or join(dirname(__file__), 'cv_video.ui')
        self.webcamIndex = webcamIndex
        self.webcamInitialResolution = webcamInitialResolution

    def __enter__(self):
        # Load in the GUI.
        uic.loadUi(self.uiFile, self)

        # Open a webcam.
        self.cap = cv2.VideoCapture(self.webcamIndex)
        assert self.cap.isOpened()

        # Scan for possible resolutions from a list of common resolutions.
        self.supported_resolution = []
        for resolution in (
          # 16:9 aspect ratio:
          (1920, 1080),
          (1280, 720),
          # 4:3 aspect ratio:
          (1024, 768),
          (640, 480) ):

            self.cap.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, resolution[0])
            self.cap.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, resolution[1])

            if (self.cap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH) == resolution[0] and
                self.cap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT) == resolution[1]):
                self.supported_resolution.append(resolution)
                self.cbWebcamResolution.addItem('{}x{}'.format(resolution[0],
                  resolution[1]), resolution)

        if self.webcamInitialResolution < 0:
            self.webcamInitialResolution = len(self.supported_resolution) - 1
        self.cbWebcamResolution.setCurrentIndex(self.webcamInitialResolution)

        # Set up a timer to read from the webcam.
        self.webcamTimer = QTimer(self)
        self.webcamTimer.setInterval(0)
        self.webcamTimer.timeout.connect(self._on_webcamTimer_timeout)
        self.webcamTimer.start()

        # Monitor the fps.
        self.fpsLabel = QLabel()
        self.statusBar().addPermanentWidget(self.fpsLabel)
        self.fpsTimer = QElapsedTimer()
        self.fpsTimer.start()

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.cap.release()
        self.webcamTimer.timeout.disconnect(self._on_webcamTimer_timeout)
        self.webcamTimer.stop()

    @pyqtSlot(int)
    def on_cbWebcamResolution_currentIndexChanged(self,
      # The index of the current item in the combobox
      index):

        resolution = self.cbWebcamResolution.itemData(index)
        self.cap.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, resolution[0])
        self.cap.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, resolution[1])


    @pyqtSlot()
    def _on_webcamTimer_timeout(self):
        # Get a frame from the webcam.
        success_flag, cvImage = self.cap.read()
        assert success_flag

        self._processImage(cvImage)

        self.fpsLabel.setText('{} fps'.format(round(1000.0/self.fpsTimer.elapsed())))
        self.fpsTimer.restart()

    # This routine is called whenever a webcam image is available to process. It
    # should also display the resulting image.
    def _processImage(self,
      # The OpenCV image to process.
      cvImage):

        # Don't process; to demonstrate, simply display the image.
        cvImageToQt(cvImage, self.lOrig)
#
# Main
# ====
def main(mainWindow, *args, **kwargs):
    app = QApplication(sys.argv)
    with mainWindow(*args, **kwargs) as window:
        window.show()
        status = app.exec_()

if __name__ == "__main__":
    main(MainWindow)
