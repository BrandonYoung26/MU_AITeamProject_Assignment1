# MU_AITeamProject_Assignment1

## interbox launch
ros2 launch interbotix_xsarm_moveit xsarm_moveit.launch.py robot_model:=rx200 hardware_type:=actual

## Parce Test Call
ros2 service call /pose_coords custom_interfaces/srv/PoseCoords "{start_pos: [0,1,2], goal_pos: [3,4,5]}"

