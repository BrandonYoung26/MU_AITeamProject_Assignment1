from setuptools import find_packages, setup

package_name = 'rx200_moveit_client'

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
    description='The ros2 moveit action client to control the interbotix rx200 robotic arm and gripper with custom service commands',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'rx200_moveit_control=rx200_moveit_client.rx200_moveit_client_node:main',
        ],
    },
)
