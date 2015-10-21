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
    cap.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 1920);
    cap.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 1080);

    delta_t = .03

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

        cv2.imshow("Direct from webcam", image)

        # Convert the image to 32-bit floating point: divide by 255, since the range is between 0 and 1, not 0 and 255.
        float_image = image/np.float32(255.0)

        # Reduce the gamma of the image by 1 stop (a factor of 1/2^1).
        diff_image = float_image*np.float32((0.5, 0.5, 0.5))
        draw_str(diff_image, (0, 10), "{} fps".format(round(1.0/delta_t)))
        cv2.imshow("Diff image", diff_image)
        delta_t = timeit.default_timer() - t_start

    # Free resources.
    cap.release()
    cv2.destroyAllWindows()

# This routine places a string at the given location in an image. It was taken from openCV, in python2/samples/common.py.
def draw_str(dst, (x, y), s):
    cv2.putText(dst, s, (x + 1, y + 1), cv2.FONT_HERSHEY_PLAIN, 1.0, (0, 0, 0),
                thickness = 2)
    cv2.putText(dst, s, (x, y), cv2.FONT_HERSHEY_PLAIN, 1.0, (255, 255, 255))


if __name__ == "__main__":
    main()
