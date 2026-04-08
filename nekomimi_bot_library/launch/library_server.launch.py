import os
from ament_index_python.packages import get_package_share_directory

from launch_ros.actions import Node

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, OpaqueFunction, RegisterEventHandler, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch.event_handlers import OnProcessExit

import xacro


def generate_launch_description():
    arg_robot_name = DeclareLaunchArgument('robot_name', default_value='nekomimi_bot')
    arg_enable_gz   = DeclareLaunchArgument('enable_gz', default_value='False')

    tts_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('nekomimi_bot_library'),
                'launch',
                'tts.launch.py'
            ])
        ]),
        launch_arguments={
            'namespace': LaunchConfiguration('robot_name'),
        }.items(),
    )

    stt_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('nekomimi_bot_library'),
                'launch',
                'stt.launch.py'
            ])
        ]),
        launch_arguments={
            'namespace': LaunchConfiguration('robot_name'),
        }.items(),
    )

    return LaunchDescription([
        arg_robot_name,
        arg_enable_gz,
        tts_node,
        stt_node,
    ])