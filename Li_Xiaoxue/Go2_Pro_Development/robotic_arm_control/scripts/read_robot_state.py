#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Read myCobot 280 robot state.
Only reads data and does not send motion commands.
"""

from pymycobot.mycobot import MyCobot
import time


PORT = "/dev/ttyUSB0"
BAUDRATE = 1000000


def main():
    print("Connecting to myCobot 280...")

    mc = None

    try:
        mc = MyCobot(PORT, BAUDRATE)
        time.sleep(1)

        print("\n========== Robot State ==========")

        connected = mc.is_controller_connected()
        print("Controller connected:", connected)

        if not connected:
            print("Controller communication failed.")
            return

        angles = mc.get_angles()
        print("Joint angles (degrees):", angles)

        coords = mc.get_coords()
        print("End-effector coordinates:", coords)

        moving = mc.is_moving()
        print("Robot moving:", moving)

        power = mc.is_power_on()
        print("Robot power on:", power)

        print("================================")

    except Exception as e:
        print("Failed to read robot state:", e)

    finally:
        if mc is not None:
            mc.close()
            print("\nSerial connection closed.")


if __name__ == "__main__":
    main()
