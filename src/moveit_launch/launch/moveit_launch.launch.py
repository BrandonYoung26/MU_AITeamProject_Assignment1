from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
import os
from ament_index_python import get_package_share_directory



# ========================================
#           Launch Declarations
# ========================================
def generate_launch_description():
    # Declaring if rx200 actual or fake
    rx200_var = DeclareLaunchArgument(
        'hardware_type',
        default_value='actual',
        description='RX200 robot type'
    )

    # Launch interbotix launch ifle
    rx200_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('interbotix_xsarm_moveit'),
                         'launch',
                         'xsarm_moveit.launch.py')
        ),
                         launch_arguments={'robot_model': 'rx200',
                       'hardware_type':LaunchConfiguration('hardware_type')}.items()
        )

    # Moveit action client node launch
    moveit_client = Node(
            package='rx200_moveit_client',
            executable='rx200_moveit_control',
        )

    ld = LaunchDescription()
    ld.add_entity(rx200_var)
    ld.add_action(rx200_launch)
    ld.add_action(moveit_client)
    return ld