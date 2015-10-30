#!/usr/bin/env python
# .. -*- coding: utf-8 -*-
#
# ******************************************************************
# mav_control_base - Basic setup to control an AR Drone using a GUI.
# ******************************************************************
# This provide a framework for controlling the MAV, by
# displaying and opening a simple GUI.
#
# Imports
# =======
# Library imports
# ---------------
import sys
from os.path import dirname, join
#
# Third-party imports
# -------------------
# None needed.
#
import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)

import rospy
import cv2
#from std_msgs.msg import String

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic

from geometry_msgs.msg import Twist  	 # for sending commands to the drone

from sensor_msgs.msg import Image    	 # for receiving the video feed

from cv_bridge import CvBridge  # CvBridgeError

import numpy as np

# Local imports
# -------------
from webcam_find_car import find_car
from drone_controller import BasicDroneController

from sensor_msgs.msg import Joy


# Some Constants
COMMAND_PERIOD = 100 #ms

# Gui Controller
class ButtonGui(QDialog):
    def __init__(self):
        # Always do Qt init first.
        QDialog.__init__(self)

        self.controller = BasicDroneController()

        # Set up the user interface from Designer.

        uic.loadUi(join(dirname(__file__), 'mav_control.ui'), self)
        self.setWindowTitle('AR.Drone Video Feed')
        self.cv = CvBridge()

        self.trackingColor = np.array([1, 0, 0], dtype=np.float32)
#       import cProfile
#	self._pr = cProfile.Profile()

    def callback(self, joy):
        print("hi")
        if joy.buttons[7] == 1:
            print('Takeoff')
            self.controller.SendTakeoff()
            
        if joy.buttons[6] == 1:
            print('Land')
            self.controller.SendLand()
            
        if joy.buttons[0] == 1:
            print('LED')
            self.controller.SetLedAnimation(3, 5, 3)
            
        if joy.buttons[1] == 1:
            print('Flat Trim')
            self.controller.SetFlatTrim()
            
        if joy.buttons[2] == 1:
            print('Toggle Camera')
            self.controller.ToggleCamera()
            
        if joy.buttons[3] == 1:
            print('Emergency')
            self.controller.SendEmergency()
            
        if joy.axes[0] >= 0.5:
            print('Left')
            self.controller.SetCommand(roll=0.3,pitch=0, yaw_velocity=0, z_velocity=0)
            
        if joy.axes[0] < -0.5:
            print('Right')
            self.controller.SetCommand(roll=-0.3,pitch=0, yaw_velocity=0, z_velocity=0)
            
        if joy.axes[1] >= 0.5:
            print('Forward')
            self.controller.SetCommand(roll=0,pitch=0.3, yaw_velocity=0, z_velocity=0)
            
        if joy.axes[1] < -0.5:
            print('Backward')
            self.controller.SetCommand(roll=0,pitch=-0.3, yaw_velocity=0, z_velocity=0)
            
        if joy.axes[3] >= 0.5:
            print('Rotate Left')
            self.controller.SetCommand(roll=0,pitch=0, yaw_velocity=0.3, z_velocity=0)
            
        if joy.axes[3] < -0.5:
            print('Rotate Right')
            self.controller.SetCommand(roll=0,pitch=0, yaw_velocity=-0.3, z_velocity=0)
            
        if joy.axes[4] >= 0.5:
            print('Up')
            self.controller.SetCommand(roll=0,pitch=0, yaw_velocity=0, z_velocity=0.3)
            
        if joy.axes[4] < -0.5:
            print('Down')
            self.controller.SetCommand(roll=0,pitch=0, yaw_velocity=0, z_velocity=-0.3)
            
        else:
            self.controller.hover()
            
    def videoFrame(self, image):
        self.cv_image = self.cv.imgmsg_to_cv2(image, "rgb8")
        self.cv_image = cv2.resize(self.cv_image, (self.cv_image.shape[1]/2, self.cv_image.shape[0]/2))
#	self._pr.enable()
        lab_img, cont_image, center_mass, cont_area = find_car(self.cv_image, self.trackingColor, self.hsThreshold.value()/100.0)
#	self._pr.disable()
#	self._pr.print_stats('cumtime')

        qi = QImage(cont_image.data, cont_image.shape[1], cont_image.shape[0], QImage.Format_RGB888)

        self.lbVideo.setFixedHeight(cont_image.shape[0])
        self.lbVideo.setFixedWidth(cont_image.shape[1])
        self.lbVideo.setPixmap(QPixmap.fromImage(qi))

        x_center = center_mass[0]
        y_center = center_mass[1]

        if self.cbAuto.isChecked():
            self.fly(x_center, y_center, cont_area)
        else:
            self.lbAuto.setText('Disabled.')

    def fly(self, x_center, y_center, cont_area):
        pass

    # On a mouse press, select a tracking color.
    def mousePressEvent(self, QMouseEvent):
        x = QMouseEvent.x() - self.lbVideo.x()
        y = QMouseEvent.y() - self.lbVideo.y()
        # Only pick a color if the mouse click lies inside the image.
	if x >= 0 and y >= 0 and x < self.lbVideo.width() and y < self.lbVideo.height():
            self.trackingColor = np.array(self.cv_image[y, x], dtype=np.float32)/255.0


class RosVideo(QObject):
    videoFrame = pyqtSignal(Image)
    xboxInput = pyqtSignal(Joy)

    def __init__(self):
        QObject.__init__(self)

    def run(self):
        self.sub = rospy.Subscriber('/ardrone/image_raw',
          Image, self.videoFrame.emit, queue_size=1)
        self.sub1 = rospy.Subscriber('joy', Joy, self.xboxInput.emit, queue_size = 1)

# Setup the application
def main(gui=ButtonGui):

    rospy.init_node("visual_processor", anonymous=True)

    app = QApplication(sys.argv)
    window = gui()
    window.show()

    rv = RosVideo()
    rv.videoFrame.connect(window.videoFrame)
    rv.xboxInput.connect(window.callback)
    rv.run()

    # executes the QT application
    status = app.exec_()

    # Stop receiving messages when the windows closes; otherwise,
    # see segfaults.
    rv.sub.unregister()
    sys.exit(status)

if __name__=='__main__':
    main()
