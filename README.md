# MU_AITeamProject_Assignment1

## interbox launch

ros2 launch interbotix_xsarm_moveit xsarm_moveit.launch.py robot_model:=rx200 hardware_type:=actual

## Parce Test Call

ros2 service call /pose_coords custom_interfaces/srv/PoseCoords "{start_pos: [0,1,2], goal_pos: [3,4,5]}"

## Using Git

git status                  # status of your repo

git add .                   # adds everything to commit (can specify folder/file instead of .)

git commit -m "message"     # commit and add message

git push                    # pushes commit to git repo

git pull                    # update your local repo
