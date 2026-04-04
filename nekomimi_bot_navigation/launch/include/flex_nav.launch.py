import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node

def generate_launch_description():
    package_dir = get_package_share_directory('nekomimi_bot_navigation')

    param_file_path = PathJoinSubstitution([
        package_dir, 'config', 'nav2_config.yaml'
    ])

    return LaunchDescription([
        Node(
            package='flex_nav',
            executable='head_controller_node',
            name='head_controller_node',
            output='screen',
            parameters=[param_file_path]
        ),
        Node(
            package='flex_nav',
            executable='head_angle_publisher_node',
            name='head_angle_publisher_node', 
            output='screen',
            parameters=[param_file_path]
        )
    ])