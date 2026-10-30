# MU_AITeamProject_Assignment1
Msc Robotics and Embedded AI - AITeamProject Assignment 1

# IMPLEMENTATION

The first problem was that the robot’s waist wouldn’t rotate, so only points straight ahead worked. The orientation constraints forced the gripper to face forward, so the arm couldn’t turn toward points off to the side. We fixed it by computing the heading to each target with arctan2(y, x) and turning it into a yaw quaternion, so the base turns to face every point. Next, we split the control into two commands. Node 1 is the only program that talks to Moveit, through the action client,  and it offers two services. Move_command moves the arm to an (x,y,z) pose using a position constraint (a 1cm sphere) and an orientation constraints (tolerances of 0.05 rad on x and y, and 0.01rad on z), with the speed limited to 40% and the acceleration to 20% for safety, and up to 15 planning attempts in 5 seconds. Grip_command opens or closes the gripper using a joint constraint on the finger (0.35 for open, 0.0 for closed, with a 0.01 tolerence). Each service returns Moveit’s result code (1 means success). Node 2 holds the pick and place sequence: open the gripper, move above the place point at z = 0.2, lower to z = 0.03, close the gripper, lift at 0.2, move above the place point, lower to 0.03, open the gripper, lift to 0.2, and return to the home pose (0.3,0.0,0.3). it sends one command at a time and waits for each result.

Node 2 checks every input before the robot moves, so it never asks for a position the arm can’t reach. It rejects missing or non-numeric input and has a (q) option to exit. It rejects points closer than about 0.28m to the base (x^2 + y^2  < 0.08), points farther than 0.5 m (x^2 + y^2 > 0.25), a zone behind the robot (-0.4<x<0) with absolute y < 0.2), a very large y on the x = 0 (absolute y > 0.4, where the robot would tip), and points on the negative x-axis, where the heading flips between +180 degree and – 180 degree and the base behaves erratically. During the sequence, node 2 checks every steps: if a result is not 1, it stops straight away, returns to it initial position and asks for new coordinates, so the arm never carries on from a failed move. 

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

