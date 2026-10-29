# MU_AITeamProject_Assignment1
Msc Robotics and Embedded AI - AITeamProject Assignment 1

# TODO: IMPLEMENTATION

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

## Using Git

git status                  # status of your repo

git add --all               # adds everything to commit (can specify folder/file instead of .)

git commit -m "message"     # commit and add message

git push                    # pushes commit to git repo

git pull                    # update your local repo
