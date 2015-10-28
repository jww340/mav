# .. -*- coding: utf-8 -*-
#
# **********************************************************
# cv_video.py - Image processing using a webcam with OpenCV.
# **********************************************************
import timeit
import cv2
import numpy as np

def main():
    # Open a webcam.
    cap = cv2.VideoCapture(0)
    assert cap.isOpened()
    # Some typical resolutions:
    #
    # * 16:8 - 1920x1080; 1280x720
    # * 4:3 - 1024x768; 800x600; 640x480
    cap.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 480)

    delta_t = .03

    cc = CameraCalib()

    # Using `waitKey <http://docs.opencv.org/modules/highgui/doc/user_interface.html#waitkey>`_, grab a frame then process it.
    isDone = False
    while not isDone:
        # Wait the minimum amount of time (1 ms) for the user to press a key. This also updates the window contents.
        key = cv2.waitKey(1)

        t_start = timeit.default_timer()

        # Quit if the user presses the Esc key.
        isDone = key == 27

        # Get a frame from the webcam.
        success_flag, image = cap.read()
        assert success_flag

        # Resize it to half size.
        sz = image.shape
        #image = cv2.resize(image, (sz[1], sz[0]))


        if key == 32:
            calib_image = image.copy()
            cc.process_frame(calib_image)
            cv2.imshow("Calib image", calib_image)

        draw_str(image, (0, 10), "{} fps".format(round(1.0/delta_t)))
        cv2.imshow("Direct from webcam", image)
        delta_t = timeit.default_timer() - t_start

    # Free resources.
    cap.release()
    cv2.destroyAllWindows()

# This routine places a string at the given location in an image. It was taken from openCV, in python2/samples/common.py.
def draw_str(dst, (x, y), s):
    cv2.putText(dst, s, (x + 1, y + 1), cv2.FONT_HERSHEY_PLAIN, 1.0, (0, 0, 0),
                thickness=2)
    cv2.putText(dst, s, (x, y), cv2.FONT_HERSHEY_PLAIN, 1.0, (255, 255, 255))


# Taken from http://docs.opencv.org/master/dc/dbb/tutorial_py_calibration.html.
class CameraCalib(object):
    def __init__(self):
        # termination criteria
        self.criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

        # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ..., (6,5,0)
        self.objp = np.zeros((6*7, 3), np.float32)
        self.objp[:, :2] = np.mgrid[0:7, 0:6].T.reshape(-1, 2)

        # Arrays to store object points and image points from all the images.
        self.objpoints = [] # 3d point in real world space
        self.imgpoints = [] # 2d points in image plane.

    def process_frame(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Find the chess board corners
        ret, corners = cv2.findChessboardCorners(gray, (9, 6), None)

        # If found, add object points, image points (after refining them)
        if ret:
            self.objpoints.append(self.objp)

            cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), self.criteria)
            self.imgpoints.append(corners)

            # Draw and display the corners
            cv2.drawChessboardCorners(image, (9, 6), corners, ret)



if __name__ == "__main__":
    main()
