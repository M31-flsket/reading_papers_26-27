
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
myCobot 280 low-level driver.
Provides serial communication, state reading and safe joint control.
"""

import time
from pymycobot.mycobot import MyCobot


class MyCobotDriver:
    """Low-level driver for myCobot 280."""

    # Conservative software limits for initial development.
    JOINT_LIMITS = {
        1: (-90, 90),
        2: (-60, 60),
        3: (-90, 90),
        4: (-90, 90),
        5: (-90, 90),
        6: (-90, 90)
    }

    def __init__(self, port="/dev/ttyUSB0", baudrate=1000000):
        self.port = port
        self.baudrate = baudrate
        self.mc = None

    def connect(self):
        """Connect to the robot controller."""
        if self.mc is not None:
            return self.is_connected()

        print("Connecting to myCobot 280...")

        self.mc = MyCobot(self.port, self.baudrate)
        time.sleep(1)

        if self.is_connected():
            print("Robot controller connected.")
            return True

        print("Robot controller connection failed.")
        self.disconnect()
        return False

    def disconnect(self):
        """Close the serial connection."""
        if self.mc is not None:
            self.mc.close()
            self.mc = None
            print("Serial connection closed.")

    def _check_connection(self):
        if self.mc is None:
            raise RuntimeError("Robot is not connected.")

    def is_connected(self):
        if self.mc is None:
            return False
        return self.mc.is_controller_connected()

    
    def get_angles(self, retries=3):
        """Read six joint angles with retry protection."""
        self._check_connection()

        for attempt in range(retries):
            angles = self.mc.get_angles()

            if angles is not None and len(angles) == 6:
                return angles

            print("Warning: Failed to read joint angles. Retry {}/{}".format(
                attempt + 1, retries
            ))

            time.sleep(0.3)

        raise RuntimeError("Failed to read valid joint angles after retries.")


    def get_coords(self):
        """Read end-effector coordinates."""
        self._check_connection()
        return self.mc.get_coords()

    def is_moving(self, retries=3):
        """Read robot motion status with retry protection."""
        self._check_connection()

        for attempt in range(retries):
            status = self.mc.is_moving()

            if status == 0 or status == 1:
                return status

            print("Warning: Invalid motion status. Retry {}/{}".format(
                attempt + 1, retries
            ))

            time.sleep(0.3)

        raise RuntimeError(
            "Failed to read valid robot motion status after retries."
        )

    def is_power_on(self):
        self._check_connection()
        return self.mc.is_power_on()

    def get_robot_state(self):
        """Read the complete robot state."""
        self._check_connection()

        return {
            "connected": self.is_connected(),
            "angles": self.get_angles(),
            "coords": self.get_coords(),
            "moving": self.is_moving(),
            "power_on": self.is_power_on()
        }

    def check_joint_limit(self, joint_id, target_angle):
        """Check whether a target angle is within software limits."""
        if joint_id not in self.JOINT_LIMITS:
            raise ValueError("Invalid joint ID. Use 1 to 6.")

        minimum, maximum = self.JOINT_LIMITS[joint_id]

        if not minimum <= target_angle <= maximum:
            raise ValueError(
                "J{} target {} is outside software limits [{}, {}].".format(
                    joint_id, target_angle, minimum, maximum
                )
            )

        return True

    def send_angle(self, joint_id, target_angle, speed=10):
        """Move one joint to an absolute target angle."""
        self._check_connection()

        if not isinstance(speed, (int, float)) or not 1 <= speed <= 100:
            raise ValueError("Speed must be between 1 and 100.")

        self.check_joint_limit(joint_id, target_angle)

        current_angles = self.get_angles()

        if current_angles is None or len(current_angles) != 6:
            raise RuntimeError("Unable to read all six joint angles.")

        moving = self.is_moving()

        if moving != 0:
            raise RuntimeError(
                "Robot motion status is not confirmed as stopped."
            )

        print("Joint {} current angle: {:.2f}".format(
            joint_id, current_angles[joint_id - 1]
        ))
        print("Joint {} target angle: {:.2f}".format(
            joint_id, target_angle
        ))
        print("Movement speed:", speed)

        return self.mc.send_angle(joint_id, target_angle, speed)

    def stop(self):
        """Send stop command to the robot."""
        self._check_connection()

        print("Sending robot stop command...")

        return self.mc.stop()
