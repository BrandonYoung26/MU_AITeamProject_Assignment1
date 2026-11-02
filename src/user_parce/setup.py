from setuptools import find_packages, setup

package_name = 'user_parce'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Brandon Young',
    maintainer_email='Brandon.young.2027@mumail.ie',
    description='ROS2 Node to take pick and place user inputs and send to RX200 Moveit Action Client using custom_interfaces',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'send_pose = user_parce.send_pose_service_node:main',
        ],
    },
)
