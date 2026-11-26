
# myCobot 280 Robotic Arm Development

## Stage 01 — Basic Communication, State Reading and Joint Control

**Date:** 2026-11-26  
**Platform:** Yahboom JetCobot  
**Robot:** Elephant Robotics myCobot 280 for Arduino

---

## 1. Project Overview

本项目基于 Yahboom JetCobot 平台和 Elephant Robotics myCobot 280 for Arduino 六自由度机械臂，开发自主机械臂控制系统。

项目采用 Python + ROS 分层开发架构，逐步实现：

- 机械臂底层通信与控制
- 关节状态读取与运动控制
- 正向运动学与逆向运动学
- 轨迹规划与运动控制
- 视觉识别与目标定位
- 自主抓取
- 与 Unitree Go2 四足机器狗协同控制

本阶段主要目标是建立自主 Python 控制项目，验证 Jetson Nano 与机械臂之间的通信，并完成第一次单关节小幅度运动测试。

---

## 2. Hardware Configuration

| Hardware | Configuration |
|---|---|
| Robotic Arm | myCobot 280 for Arduino |
| Manufacturer | Elephant Robotics |
| Degrees of Freedom | 6 |
| End Effector | Two-finger gripper |
| Main Controller | NVIDIA Jetson Nano B01 |
| Power Supply | DC 12V, 60W |
| Communication | Serial |
| Serial Port | `/dev/ttyUSB0` |
| Baudrate | `1000000` |

---

## 3. Software Environment

| Component | Version / Configuration |
|---|---|
| Operating System | Ubuntu 18.04.6 LTS |
| Kernel | Linux 4.9.253-tegra |
| Architecture | aarch64 |
| Python | 3.6.9 |
| ROS | ROS Melodic |
| pymycobot | 3.4.6 |
| OpenCV | Original system environment |

### Development Environment

- Windows PC
- VS Code
- VS Code Remote - SSH
- Jetson Nano remote development

通过 SSH 和 VS Code Remote - SSH，可以直接在 Windows 电脑上编辑和运行 Jetson Nano 中的 Python 程序。

---

## 4. Original System Inspection

在开发自主控制程序之前，对 Jetson Nano 原厂系统进行了检查。

原厂 ROS 工作空间：

```text
~/jetcobot_ws/
```

主要功能包包括：

- `jetcobot_ctrl`：机械臂控制
- `jetcobot_description`：机械臂模型描述
- `jetcobot_moveit`：MoveIt 相关功能
- `jetcobot_moveit_config`：MoveIt 配置
- `jetcobot_grasp`：抓取功能
- `jetcobot_visual`：视觉相关功能
- `jetcobot_color_follow`：颜色跟踪
- `jetcobot_face_follow`：人脸跟踪

检查了原厂手柄控制程序 `yahboom_joy.py`，确认其使用：

```python
from pymycobot.mycobot import MyCobot

mc = MyCobot('/dev/ttyUSB0', 1000000)
```

原厂程序通过 pymycobot SDK 控制机械臂。

本项目暂时保留原厂系统和驱动，不直接修改原厂程序。

---

## 5. Custom Development Project

自主开发项目位于：

```text
~/mycobot_dev/
```

当前目录结构：

```text
robotic_arm_control/
├── README.md
├── robot/
│   ├── __init__.py
│   └── mycobot_driver.py
└── scripts/
    ├── test_connection.py
    ├── read_robot_state.py
    ├── test_driver.py
    └── test_joint_motion.py
```

### 5.1 Architecture

项目采用分层设计：

| Layer | Responsibility |
|---|---|
| Hardware | myCobot 280 robotic arm |
| SDK | pymycobot serial communication |
| Driver | Custom low-level robot driver |
| Scripts | Connection, state reading and motion tests |
| ROS | Future robot communication and system integration |
| Application | Future motion planning, vision and grasping |

### 5.2 Custom Driver

文件：

```text
robot/mycobot_driver.py
```

自定义驱动类：

```python
MyCobotDriver
```

当前已经实现的主要接口：

| Method | Function |
|---|---|
| `connect()` | Connect to the robot controller |
| `disconnect()` | Close serial communication |
| `is_connected()` | Check controller connection |
| `get_angles()` | Read six joint angles |
| `get_coords()` | Read end-effector coordinates |
| `is_moving()` | Read robot motion status |
| `is_power_on()` | Check robot power status |
| `get_robot_state()` | Read complete robot state |
| `check_joint_limit()` | Check software joint limits |
| `send_angle()` | Control a single joint |

针对 SDK 偶尔返回 `None` 的情况，增加了关节角度和运动状态读取重试机制。

对于运动控制，增加了软件关节限位、速度参数检查和运动状态检查。

### 5.3 Software Joint Limits

当前采用较保守的软件安全限位：

```python
JOINT_LIMITS = {
    1: (-90, 90),
    2: (-60, 60),
    3: (-90, 90),
    4: (-90, 90),
    5: (-90, 90),
    6: (-90, 90)
}
```

这些数值是本项目当前采用的软件限位，不代表机械臂的全部硬件运动范围。

---

## 6. Stage 01 Development Progress

### 6.1 Remote Development Environment

已完成：

- [x] Jetson Nano SSH 远程连接
- [x] Windows 与 Jetson Wi-Fi 热点连接
- [x] VS Code Remote - SSH 连接
- [x] 原厂 ROS 工作空间检查
- [x] 原厂机械臂控制程序分析
- [x] pymycobot SDK 安装与接口检查

### 6.2 Serial Communication

创建测试程序：

```text
scripts/test_connection.py
```

使用：

```python
mc = MyCobot("/dev/ttyUSB0", 1000000)
connected = mc.is_controller_connected()
```

测试结果：

```text
Connecting to myCobot 280...
Controller connection status: 1
Serial connection closed.
```

**Result:** Serial communication successful.

### 6.3 Robot State Reading

创建测试程序：

```text
scripts/read_robot_state.py
```

成功读取：

- 控制器连接状态
- 六个关节角度
- 末端执行器坐标
- 机械臂运动状态
- 机械臂电源状态

最近一次状态读取结果：

```text
Controller connected: 1

Joint angles (degrees):
[7.47, -0.52, -0.35, -0.96, 0.26, -45.87]

End-effector coordinates:
[61.3, -56.9, 409.1, -92.64, -45.83, -80.36]

Robot moving: 0
Robot power on: 1
```

**Result:** Robot state reading successful.

### 6.4 Custom Driver Validation

创建测试程序：

```text
scripts/test_driver.py
```

通过自定义 `MyCobotDriver` 成功完成：

- 串口连接
- 控制器状态检查
- 关节角度读取
- 末端坐标读取
- 运动状态读取
- 电源状态读取
- 串口断开

**Result:** Custom driver basic functions validated.

### 6.5 Single Joint Motion Test

创建测试程序：

```text
scripts/test_joint_motion.py
```

本阶段选择 J1 进行小幅度运动测试。

#### Test Parameters

| Parameter | Value |
|---|---:|
| Joint ID | J1 |
| Initial Angle | 7.47° |
| Target Angle | 12.47° |
| Commanded Angle Change | +5° |
| Speed | 10 |

#### Test Output

```text
Connecting to myCobot 280...
Robot controller connected.

========== Motion Test ==========
Joint: 1
Current angle: 7.47
Target angle: 12.469999999999999
Angle change: 5
Speed: 10
=================================

Starting motion...
Joint 1 current angle: 7.47
Joint 1 target angle: 12.47
Movement speed: 10

Waiting for joint movement...
Joint movement detected.
Target position reached and stable.

========== Motion Result ==========
Target angle: 12.469999999999999
Final angle: 11.51
Angle error: 0.96
===================================
Serial connection closed.
```

#### Test Result Analysis

| Item | Result |
|---|---:|
| Initial Angle | 7.47° |
| Target Angle | 12.47° |
| Final Angle | 11.51° |
| Actual Angle Change | +4.04° |
| Position Error | 0.96° |
| Movement Detected | Yes |
| Position Stability Check | Passed |

当前程序使用以下条件判断目标位置：

```python
abs(target_angle - current_angle) <= 1.0
```

并要求连续三次满足该误差条件。

本次测试中，最终角度误差为 0.96°，符合当前程序设定的到位判断条件。

需要注意：这只说明机械臂到达目标位置附近，并通过了当前的位置容差检查，不代表已经实现高精度定位控制。

**Result:** J1 small-angle motion test successful.

---

## 7. Current Development Status

| Development Item | Status |
|---|---|
| SSH Remote Development | Completed |
| Original System Inspection | Completed |
| SDK Verification | Completed |
| Serial Communication | Completed |
| Robot State Reading | Completed |
| Custom Python Driver | Basic implementation completed |
| Single Joint Motion | Initial test successful |
| Gripper Control | Not started |
| Forward Kinematics | Not started |
| Inverse Kinematics | Not started |
| Trajectory Planning | Not started |
| ROS Integration | Not started |
| Visual Recognition | Not started |
| Autonomous Grasping | Not started |

---

## 8. Next Development Stage

下一阶段将继续完善自主机械臂控制系统。

计划任务：

1. 完善单关节运动控制接口。
2. 优化运动完成判断和角度误差检测。
3. 测试其他关节的小幅度运动。
4. 实现多关节联合控制。
5. 实现夹爪开合控制。
6. 研究机械臂正向运动学。
7. 建立机械臂运动学模型。

后续逐步接入 ROS Melodic，研究 MoveIt 运动规划和视觉抓取。

---

## 9. Safety Notes

机械臂运动测试期间需要注意：

- 运动前确认机械臂周围没有障碍物。
- 测试过程中手不要放在关节、连杆和夹爪附近。
- 初期采用小角度、低速度测试。
- 运动指令发送前检查机械臂状态。
- 软件限位不能代替硬件限位和物理急停。
- 发生异常时，应使用物理急停或切断控制箱电源。

---

## 10. Stage Summary

本阶段完成了 myCobot 280 自主控制开发的基础工作。

从原厂系统检查开始，完成了 Jetson Nano 远程开发环境搭建、pymycobot SDK 验证、自定义 Python 驱动编写、机械臂状态读取，以及 J1 单关节 5° 小幅度运动测试。

目前已经初步建立了：

**Jetson Nano → pymycobot SDK → Custom Python Driver → myCobot 280**

这一基础控制链路。

下一阶段将在此基础上继续完善关节控制、夹爪控制和运动学功能，为后续 ROS 集成、视觉抓取以及与 Unitree Go2 的协同控制做准备。

---

**Stage 01 Completed — Basic Communication, State Reading and Joint Motion Validation.**

