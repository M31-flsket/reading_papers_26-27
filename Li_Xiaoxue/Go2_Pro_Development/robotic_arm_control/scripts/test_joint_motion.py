#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test a small movement of one myCobot joint.
J1 moves 5 degrees from its current position.
"""

import sys
import os
import time

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
sys.path.insert(0, PROJECT_ROOT)

from robot.mycobot_driver import MyCobotDriver


JOINT_ID = 1
ANGLE_STEP = 5
SPEED = 10

POLL_INTERVAL = 0.5
TIMEOUT = 15


def main():
    robot = MyCobotDriver()

    try:
        if not robot.connect():
            print("Failed to connect to robot.")
            return

        state = robot.get_robot_state()

        if state is None:
            raise RuntimeError("Failed to read robot state.")

        if not state["connected"]:
            raise RuntimeError("Controller is disconnected.")

        if state["moving"] != 0:
            raise RuntimeError("Robot is moving. Test cancelled.")

        if not state["power_on"]:
            raise RuntimeError("Robot power is off.")

        angles = state["angles"]

        if not isinstance(angles, (list, tuple)) or len(angles) != 6:
    	    raise RuntimeError("Invalid joint angle data.")

        current_angle = angles[JOINT_ID - 1]
        target_angle = current_angle + ANGLE_STEP

        print("\n========== Motion Test ==========")
        print("Joint:", JOINT_ID)
        print("Current angle:", current_angle)
        print("Target angle:", target_angle)
        print("Angle change:", ANGLE_STEP)
        print("Speed:", SPEED)
        print("=================================")

        robot.check_joint_limit(JOINT_ID, target_angle)

        # Check the current state again immediately before motion.
        angles = robot.get_angles()

        if angles is None or len(angles) != 6:
            raise RuntimeError("Failed to verify current joint angles.")

        if robot.is_moving() != 0:
            raise RuntimeError("Robot started moving. Test cancelled.")

        if abs(angles[JOINT_ID - 1] - current_angle) > 1.0:
            raise RuntimeError("Joint position changed. Test cancelled.")

        print("\nStarting motion...")
        robot.send_angle(JOINT_ID, target_angle, SPEED)

        start_time = time.time()
        motion_started = False
        stable_count = 0
        final_angles = None

        print("\nWaiting for joint movement...")

        while time.time() - start_time < TIMEOUT:
            time.sleep(POLL_INTERVAL)

            angles = robot.get_angles()

            current = angles[JOINT_ID - 1]

            # Detect actual joint movement.
            if not motion_started:
                if abs(current - current_angle) >= 0.3:
                    motion_started = True
                    print("Joint movement detected.")

            # Check whether the joint has reached the target.
            if motion_started:
                error = abs(target_angle - current)

                if error <= 1.0:
                    stable_count += 1
                else:
                    stable_count = 0

                if stable_count >= 3:
                    final_angles = angles
                    print("Target position reached and stable.")
                    break

        if not motion_started:
            raise RuntimeError(
                "Joint movement was not detected. "
                "Please inspect the robot."
            )

        if final_angles is None:
            raise RuntimeError(
                "Motion timeout or target position not reached. "
                "Please inspect the robot."
            )

        final_angle = final_angles[JOINT_ID - 1]

        print("\n========== Motion Result ==========")
        print("Target angle:", target_angle)
        print("Final angle:", final_angle)
        print("Angle error:", round(target_angle - final_angle, 2))
        print("===================================")

    except Exception as e:
        print("Motion test failed:", e)

        # Attempt to stop the robot after an error.
        if robot.mc is not None:
            try:
                robot.stop()
                print("Stop command sent.")
                time.sleep(0.5)
            except Exception as stop_error:
                print("Failed to send stop command:", stop_error)
                print("Use the physical emergency stop or cut power if necessary.")

    finally:
        robot.disconnect()


if __name__ == "__main__":
    main()

