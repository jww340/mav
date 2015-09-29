# .. -*- coding: utf-8 -*-
#
# **********************************************************
# mav_gui.py - MAV recharging with a GUI, implemented in Qt.
# **********************************************************
#
# Imports
# =======
# Library
# -------
import sys
from os.path import dirname, join
from time import sleep
#
# Third-party
# -----------
# Use "Pythonic" (and PyQt5-compatible) `glue classes <http://pyqt.sourceforge.net/Docs/PyQt4/incompatible_apis.html>`_. This must be done before importing from PyQt4.
import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)

from PyQt4.QtGui import QApplication, QDialog, QIntValidator
from PyQt4.QtCore import QTimer, QThread, QObject, pyqtSignal
from PyQt4 import uic
#
class DummyWorker(QObject):
    run = pyqtSignal(float)

    def __init__(self, parent):
        # First, let the QDialog initialize itself.
        super(DummyWorker, self).__init__()
        self.parent = parent

    def when_run(self, time_sec):
        print("sleeping for {} seconds.".format(time_sec))
        sleep(time_sec)
        self.parent.hsChargeTime.setValue.emit(50)
#
# Implement a dialog box.
# =======================
class MyDialog(QDialog):
    def __init__(self):
        # First, let the QDialog initialize itself.
        super(MyDialog, self).__init__()

        # `Load <http://pyqt.sourceforge.net/Docs/PyQt4/designer.html#PyQt4.uic.loadUi>`_ in our UI. The secord parameter lods the resulting UI directly into this class.
        uic.loadUi(join(dirname(__file__), 'mav_gui.ui'), self)

        # Only allow numbers between 0 and 99 for the lien edits.
        flyTimeValidator = QIntValidator(0, 99, self)
        self.leFlyTime.setValidator(flyTimeValidator)

        # Create a separate thread
        self._thread = QThread()
        self._thread.start()
        # Create a worker.
        self._worker = DummyWorker(self)
        self._worker.moveToThread(self._thread)
        self._worker.run.connect(self._worker.when_run)



##        QTimer.singleShot(10500, self._onTimeout)
##        self._timer = QTimer(self)
##        self._timer.timeout.connect(self._onTimeout)
##        self._timer.start(1500)
##
##    def _onTimeout(self):
##        self.hsFlyTime.setValue(50)
    def on_hsFlyTime_valueChanged(self, value):
        self.leFlyTime.setText(str(value))
        self._worker.run.emit(1.5)

    def on_leFlyTime_editingFinished(self):
        self.hsFlyTime.setValue(int(self.leFlyTime.text()))

    def close(self):
        super(MyDialog, self).close()
        self._thread.quit()
        self._thread.wait()
        print("hi")
#
# Main
# ====
def main():
    # Initialize the program. A `QApplication <http://doc.qt.io/qt-4.8/qapplication.html>`_ must always be created.
    qa = QApplication(sys.argv)
    # Construct the UI: either a `QDialog <http://doc.qt.io/qt-4.8/qdialog.html>`_ or a `QMainWindow <http://doc.qt.io/qt-4.8/qmainwindow.html>`_.
    md = MyDialog()
    # The UI is hidden while it's being set up. Now that it's ready, it must be manually shown.
    md.show()

    # Main loop.
    qa.exec_()

##    md._timer.stop()

if __name__ == '__main__':
    main()
