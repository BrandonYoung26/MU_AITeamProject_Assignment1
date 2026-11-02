# MU_AITeamProject_Assignment1
Msc Robotics and Embedded AI - AITeamProject Assignment 1

# IMPLEMENTATION

The system architecture consists of two ROS2 nodes which communiucate through custom services. 

The first node, the MoveIt control node, works as an interface with MoveIt. It uses an action client to submit motion planning requests and execution requests to the MoveIt action server, and then provides two services, one to control the robot's end effector position, and another for opening and closing the gripper. Each of the services return the MoveIt result code to show whether the operation request was succesful.

The second node, the user command and sequencing node, gives the user interface and organises the pick and place task. It takes the desired start and end coordinates, ensures that they are valid, and sends the arm and gripper commands to the MoveIt contol node. All of the service requests are expected before the next command is given, which ensures that the sequence only continues after the last operation has finished successfully.

The initil task overcome was robot's base rotation. Initially the robot was only able to move along the x-axis path because of an orientation constraint making the gripper orientation forward fixed. This was fixed this by calculating the path to each target with arctan2(y,x) and turning it into a yaw quaternion, so the base turns to face every point. The result allowed the robot to rotate towards the end coordinates while keeping the end effector in the desired orientation. 

The end effector is constrained to a sphere area of 1cm radius around the target position. Additionally, there is orientation tolerance added to constrain the robot to the desired orientation, and joint constraints applied as to control the gripper position. The velocity and acceleration factors were also reduced to have more control over the robot while its moving, and to increase the safety.

Before any movements are sent, the user command node first validates every input given by the user. Any entered coordinates that are either too close to the robot's base or out of the robot's reach, in the blocked zone behind the robot, or points on the negative x-axis (as it was found that the robot would behave erratically) are rejected. If any step in the sequence fails, the sequence stops and moves back to it initial position and asks for new coordinates. 

## Launch Steps:
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

