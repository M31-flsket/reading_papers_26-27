#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test the custom myCobot driver.
"""

import sys
import os

# Add project root to Python module search path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from robot.mycobot_driver import MyCobotDriver


def main():
    robot = MyCobotDriver()

    try:
        if not robot.connect():
            print("Failed to connect to robot.")
            return

        state = robot.get_robot_state()

        print("\n========== Robot State ==========")
        print("Connected:", state["connected"])
        print("Joint angles:", state["angles"])
        print("End-effector coordinates:", state["coords"])
        print("Moving:", state["moving"])
        print("Power on:", state["power_on"])
        print("================================")

    except Exception as e:
        print("Driver test failed:", e)

    finally:
        robot.disconnect()


if __name__ == "__main__":
    main()
