# .. -*- coding: utf-8 -*-
#
# ***********************************************************
# mav_recharging.py - Simulate a multi-MAV recharging station
# ***********************************************************
# A group of *n* MAVs each carry out a mission by taking off, flying along a directed path, then landing when the mission is complete. They land at a charging station, which is a circle with a series of electrodes evenly distributed around it. The MAVs then connect to two electrodes, charge, then take off to complete their next mission.
#
# Your task is to simulate the charging station's operation. When an MAV lands, it will reqest two electrodes from the charging station; when both are given, it charges, releases the electrodes, then takes off again. You must insure that a given electrode is only granted to one MAV at a time.
#
# Each MAV should be simulated by a class which runs in a unique thread, making charging requests of the station..
#
# Library imports
# ===============
# For the core code.
from threading import Thread, Lock
# For testing.
from time import sleep
from Queue import Queue
#
# A simple enumerate I like, taken from one of the snippet on `stackoverflow
# <http://stackoverflow.com/questions/36932/how-can-i-represent-an-enum-in-python>`_.
# What I want: a set of unique identifiers that will be named nicely,
# rather than printed as a number. Really, just a way to create a class whose
# members contain a string representation of their name. Perhaps the best
# solution is `enum34 <https://pypi.python.org/pypi/enum34>`_, based on `PEP
# 0435 <https://www.python.org/dev/peps/pep-0435/>`_, but I don't want an extra
# dependency just for this.
class Enum(frozenset):
    def __getattr__(self, name):
        if name in self:
            return name
        raise AttributeError

_MAV_STATES = Enum( ('Flying', 'Waiting', 'Charging') )
#
# Code
# ====
# The core code in this module.
#
# MAV class
# ---------
class MAV(Thread):
    def __init__(self,
      # The left electrode for this MAV.
      left_electrode,
      # The right electrode for this MAV.
      right_electrode,
      # .. _fly_time_sec:
      #
      # Time spent flying on a mission, in seconds.
      fly_time_sec=0.5,
      # .. _charge_time_sec:
      #
      # Time spent charging, in seconds.
      charge_time_sec=1.5,
      # Any extra args.
      **kwargs):

        # Thread's init **must** be called.
        super(MAV, self).__init__(**kwargs)

        self._left_electrode = left_electrode
        self._right_electrode = right_electrode
        self._fly_time_sec = fly_time_sec
        self._charge_time_sec = charge_time_sec
        self._state = None
        self.running = True

    def run(self):
        while (self.running):
            self._state = _MAV_STATES.Flying
            print('{} flying.'.format(self.name))
            sleep(self._fly_time_sec)

            self._state = _MAV_STATES.Waiting
            print('{} connecting to electrodes.'.format(self.name))
            with self._left_electrode, self._right_electrode:
                self._state = _MAV_STATES.Charging
                print('{} charging...'.format(self.name))
                sleep(self._charge_time_sec)

        self._state = None
#
# Electrode class
# ---------------
# An electrode, one element in a charging station.
class Electrode(object):
    def __init__(self):
        self._lock = Lock()

    # Access to Lock methods
    # ----------------------
    def acquire(self, *args, **kwargs):
        return self._lock.acquire(*args, **kwargs)

    def release(self):
        return self._lock.release()

    # Context manager
    # ---------------
    def __enter__(self):
        self._lock.acquire()

    def __exit__(self, exc_type, exc_value, traceback):
        self._lock.release()
        return False
#
# main code
# =========
def main():
    n = 10
    # Create n electrodes.
    electrode_list = []
    for i in range(n):
        electrode_list.append(Electrode())

    # Create n MAVs and launch them.
    MAV_list = []
    for i in range(n):
        MAV_list.append(MAV(electrode_list[i], electrode_list[i - 1],
                            name='MAV {}'.format(i)))
        MAV_list[i].start()

    # Let them fly some.
    sleep(10)

    # Land them all.
    for i in range(n):
        MAV_list[i].running = False
    for i in range(n):
        MAV_list[i].join()

if __name__ == '__main__':
    main()
