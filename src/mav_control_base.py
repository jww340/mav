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

        self.start_state = 0
        self.led_state = 0
        self.flatTrim_state = 0
        self.toggleCamera_state = 0
        self.emergency_state = 0
        self.land_state = 0
        self.takeoff_state = 0
        self.forward_state = 0
        self.backward_state = 0
        self.up_state = 0
        self.down_state = 0
        self.left_state = 0
        self.right_state = 0
        self.rotateLeft_state = 0
        self.rotateRight_state = 0
        self.flipLeft_state = 0
        self.flipRight_state = 0
        self.area = 0
        self.BUTTON_A = 0
        self.BUTTON_B = 1
        self.BUTTON_X = 2
        self.BUTTON_Y = 3
        self.BUTTON_LB = 4
        self.BUTTON_RB = 5
        self.BUTTON_START = 6
        self.BUTTON_SELECT = 7

        self.controller = BasicDroneController()

        # Set up the user interface from Designer.

        uic.loadUi(join(dirname(__file__), 'mav_control.ui'), self)
        self.setWindowTitle('AR.Drone Video Feed')
        self.cv = CvBridge()

        self.trackingColor = np.array([1, 0, 0], dtype=np.float32)
#       import cProfile
#	self._pr = cProfile.Profile()

    def handle(self, cont_area):
        self.area = cont_area
    
    def callback(self, joy):
        if self.led_state == 0 and joy.buttons[self.BUTTON_A] == 1:
            print('LED')
            self.controller.SetLedAnimation(3, 5, 3)
            self.led_state = 1
            
        if self.led_state == 1 and joy.buttons[self.BUTTON_A] == 0:
            self.led_state = 0
        
        if self.flatTrim_state == 0 and joy.buttons[self.BUTTON_B] == 1:
            print('Flat Trim')
            self.controller.SetFlatTrim()
            self.flatTrim_state = 1
            
        if self.flatTrim_state == 1 and joy.buttons[self.BUTTON_B] == 0:
            self.flatTrim_state = 0
        
        if self.toggleCamera_state == 0 and joy.buttons[self.BUTTON_X] == 1:
            print('Toggle Camera')
            self.controller.ToggleCamera()
            self.toggleCamera_state = 1
            
        if self.toggleCamera_state == 1 and joy.buttons[self.BUTTON_X] == 0:
            self.toggleCamera_state = 0
        
        if self.emergency_state == 0 and joy.buttons[self.BUTTON_Y] == 1:
            print('Emergency')
            self.controller.SendEmergency()
            self.emergency_state = 1
            
        if self.emergency_state == 1 and joy.buttons[self.BUTTON_Y] == 0:
            self.emergency_state = 0
            
        if self.flipLeft_state == 0 and joy.buttons[self.BUTTON_LB] == 1:
            print('Flip Left')
            self.controller.SetFlightAnimation(18, 0)
            self.flipLeft_state = 1
            
        if self.flipLeft_state == 1 and joy.buttons[self.BUTTON_LB] == 0:
            self.flipLeft_state = 0
        
        if self.flipRight_state == 0 and joy.buttons[self.BUTTON_RB] == 1:
            print('Flip Right')
            self.controller.SetFlightAnimation(19, 0)
            self.flipRight_state = 1
            
        if self.flipRight_state == 1 and joy.buttons[self.BUTTON_RB] == 0:
            self.flipRight_state = 0
        
        if self.land_state == 0 and joy.buttons[self.BUTTON_START] == 1:
            print('Land')
            self.controller.SendLand()
            self.land_state = 1
            
        if self.land_state == 1 and joy.buttons[self.BUTTON_START] == 0:
            self.land_state = 0
        
        if self.takeoff_state == 0 and joy.buttons[self.BUTTON_SELECT] == 1:
            print('Takeoff')
            self.controller.SendTakeoff()
            self.takeoff_state = 1
            
        if self.takeoff_state == 1 and joy.buttons[self.BUTTON_SELECT] == 0:
            self.takeoff_state = 0
        
        if self.area > 15000:
            self.controller.SendLand()
        
        if self.area <= 15000 and (joy.axes[0] >= 0.1 or joy.axes[1] >= 0.1 or joy.axes[3] >= 0.1 or joy.axes[4] >= 0.1 or joy.axes[0] <= -0.1 or joy.axes[1] <= -0.1 or joy.axes[3] <= -0.1 or joy.axes[4] <= -0.1):
            
            strafe = joy.axes[0] / 2.5
            throttle = joy.axes[1] / 2
            rotate = joy.axes[3] / 2.5
            vertical = joy.axes[4] / 2.5
            self.controller.SetCommand(roll = strafe, pitch = throttle, yaw_velocity = rotate, z_velocity = vertical)
        
        else:
            self.controller.SetCommand(roll = 0, pitch = 0, yaw_velocity = 0, z_velocity = 0)


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
        
        self.handle(cont_area)

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
