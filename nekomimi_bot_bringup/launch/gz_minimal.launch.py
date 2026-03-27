import os

from ament_index_python.packages import get_package_share_directory

from launch_ros.actions import Node

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution


def generate_launch_description():
    robot_name = 'nekomimi_bot'
    robot_id = 0
    bringup_pkg = robot_name + '_bringup'

    rviz_config = os.path.join(get_package_share_directory(bringup_pkg), 'rviz', 'gazebo.rviz')
    # world_file = os.path.join(get_package_share_directory('nekomimi_bot_gazebo'), 'worlds', 'nekoneko.world.xacro')
    # world_file = os.path.join(get_package_share_directory('sobits_gazebo_worlds'), 'worlds', 'rcjo2025_arena.world.xacro')
    world_file = os.path.join(get_package_share_directory('nekomimi_bot_description'), 'worlds', 'empty.sdf')

    return LaunchDescription([
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                PathJoinSubstitution([
                    os.path.join(get_package_share_directory('ros_gz_sim'),
                    'launch',
                    'gz_sim.launch.py')
                ])
            ]),
            launch_arguments={
                'gz_args' : ' -r -v 4 ' + world_file,
            }.items()
        ),

        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            arguments=[
                        "/clock" + "@rosgraph_msgs/msg/Clock" + "[ignition.msgs.Clock",
                        "/tf" + "@tf2_msgs/msg/TFMessage" + "[ignition.msgs.Pose_V",
                    ],
        ),

        # Launch Robot No. 1
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                PathJoinSubstitution([
                    os.path.join(get_package_share_directory(bringup_pkg),
                    'launch',
                    'robot.launch.py')
                ])
            ]),
            launch_arguments={
                'robot_name': robot_name if robot_id == 0 else robot_name + '_' + str(robot_id),
                'enable_gz'   : 'True',
                'robot_coords_x': '0.0', # x 
                'robot_coords_y': '0.0', # y
                'robot_coords_z': '0.0', # z
                'robot_coords_Y': '0.0', # yaw
            }.items()
        ),

        Node(
            package='rviz2',
            executable='rviz2',
            namespace=robot_name,
            name='rviz2',
            arguments=['-d', rviz_config],
            output='screen',
        ),
    ])
