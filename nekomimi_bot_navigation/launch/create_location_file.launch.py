import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    return LaunchDescription([
        ########## Customizable parameters ##########
        DeclareLaunchArgument(
            # ロボットを動かす場合true,動かさない場合false
            'use_robot', default_value='true'
        ),
        DeclareLaunchArgument(
            # mapのファイルパス
            'map', default_value=os.path.join(get_package_share_directory("nekomimi_bot_navigation"), 'map', 'map_example.yaml')
        ),
        DeclareLaunchArgument(
            'use_rviz', default_value='True'
        ),
        #############################################

        # Create Location File
        Node(
            package='nekomimi_bot_navigation',
            executable='location_setting.py',
            name='location_setting',
            output='screen',
            parameters=[
                {
                    'use_robot': LaunchConfiguration('use_robot'),
                    'robot_name': 'nekomimi_bot'
                }
            ]
        ),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(get_package_share_directory("nekomimi_bot_navigation"), 'launch', 'navigation.launch.py')),
            launch_arguments={
                'map'          : LaunchConfiguration('map'),
                'robot_name'   : 'nekomimi_bot',
                'location_file_path' : "",
                'use_rviz'     : LaunchConfiguration('use_rviz'),
            }.items(),
        ),
    ])