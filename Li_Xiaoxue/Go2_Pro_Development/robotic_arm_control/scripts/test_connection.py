#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
myCobot 280 communication test
Test serial communication without sending motion commands.
"""

from pymycobot.mycobot import MyCobot
import time


# Robot communication configuration
PORT = "/dev/ttyUSB0"
BAUDRATE = 1000000


def main():
    print("Connecting to myCobot 280...")

    try:
        mc = MyCobot(PORT, BAUDRATE)

        time.sleep(1)

        connected = mc.is_controller_connected()

        print("Controller connection status:", connected)

        mc.close()
        print("Serial connection closed.")

    except Exception as e:
        print("Connection test failed:", e)


if __name__ == "__main__":
    main()
