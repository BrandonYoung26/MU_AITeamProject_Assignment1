# MU_AITeamProject_Assignment1
Msc Robotics and Embedded AI - AITeamProject Assignment 1

# IMPLEMENTATION

Our system uses two ROS2 nodes. Node 1 is the robot driver. It is the only program that talks to Moveit, through the action client, and it offers two services: one moves the arm to an (x,y,z)pose, and the other opens or closes the gripper. Each service returns Moveit's result code, where 1 means success. Node 2 is the user interface and sequencer. It sends the pick-and-place steps to Node 1 one at a time and waits for each results.
The first problem was the waist would not rotate, because the orientation constraint forced the gripper to face forward. We fixed this by calculating the heading to each target with arctan2(y,x) and turning it into a yaw quaternion, so the base turns to face every point. Each moves uses constraints that combine a target with a tolerence: a 1 cm sphere for position, small angle tolerances for orientation, and a joint constraint for the gripper. We also slowed the arm down for safety.Node 2 checks every input before the robot moves. It rejects invalid input, points too close to the base or out of reach, the blocked zone behind the robot, and points on the negative x-axis, where the heading flips and base would move erratically. If any step in the sequence fails, the sequence stops and moves back to it initial position and asks for new coordinates.
--------
Steps:
- Ensure Interbotix pkg's installed and sourced
- colcon build
- source install/setup.bash
- Run as described below

## Primary Launch Commands
### Launch Interbotix and Action Client
Real Robot: ros2 launch moveit_launch moveit_launch.launch.py

Fake Robot: ros2 launch moveit_launch moveit_launch.launch.py hardware_type:=fake

### Launch User Interface
ros2 run user_parce send_pose 


## Secondary Launch Commands (Backups)
### Interbox launch
ros2 launch interbotix_xsarm_moveit xsarm_moveit.launch.py robot_model:=rx200 hardware_type:=actual

### Moveit Action Client
ros2 run rx200_moveit_client rx200_moveit_control 

### Launch User Interface
ros2 run user_parce send_pose 

### Manuall call move command service
ros2 service call /move_command custom_interfaces/srv/MoveCommand "{goal: [0.3, 0.2, 0.3]}"

### Manuall call move command service
ros2 service call /grip_command custom_interfaces/srv/GripCommand "{grip: false}"

## Input Coordinates
The User Parser will ask for a picking coordinate. Input two decimal values, for x and y (eg: 0.2 0.4). An error will be returned if the values are not suitable, and the user may enter new picking coordinates.

The User Parser then asks for a placing coordinate. Again, input two decimal values for x and y in the same format. An error will be returned if the values are not suitable, and the user may enter new placing coordinates.

Enter 'q' to exit the User Parser.

## Group 7 Members
Sophia "Rowan" Turner

Sai Wunna Htoo

Brandon Young

Tommy Bunokas

