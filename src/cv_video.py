# .. -*- coding: utf-8 -*-
#
# **********************************************************
# cv_video.py - Image processing using a webcam with OpenCV.
# **********************************************************
import cv2

# Grab an image then call ``update()`` until done.
def main():
    cap = cv2.VideoCapture(0)
    assert cap.isOpened()
    # Using `waitKey <http://docs.opencv.org/modules/highgui/doc/user_interface.html#waitkey>`_, grab a frame then call update on it
    isDone = False
    while not isDone:
        key = cv2.waitKey(1)
        success_flag, image = cap.read()
        assert success_flag
        sz = image.shape
        image = cv2.resize(image, (sz[1]/2, sz[0]/2))
        cv2.imshow("Direct from webcam", image)

    self.cap.release()

if __name__ == "__main__":
    main()
