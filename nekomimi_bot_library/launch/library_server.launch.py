import os
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch_ros.actions import Node

from launch.actions import DeclareLaunchArgument, OpaqueFunction, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    arg_robot_name = DeclareLaunchArgument('robot_name', default_value='nekomimi_bot')
    arg_enable_gz   = DeclareLaunchArgument('enable_gz', default_value='False')


    pose_config = os.path.join(
        get_package_share_directory("nekomimi_bot_library"),
        "config",
        "pose_list.yaml",
    )

    joint_action_server_node = Node(
        package="nekomimi_bot_library",
        executable="joint_action_server",
        name="joint_action_server",
        namespace=LaunchConfiguration('robot_name'),
        parameters=[pose_config,
            {"use_sim_time": LaunchConfiguration('enable_gz')},
        ],
        output="screen",
    )

    wheel_action_server_node = Node(
        package="nekomimi_bot_library",
        executable="wheel_action_server",
        name="wheel_action_server",
        namespace=LaunchConfiguration('robot_name'),
        parameters=[
            {"use_sim_time": LaunchConfiguration('enable_gz')},
        ],
        output="screen",
    )

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

    blockly_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('nekomimi_bot_library'),
                'launch',
                'blockly.launch.py'
            ])
        ]),
        launch_arguments={
            'blockly_namespace': LaunchConfiguration('robot_name'),
        }.items(),
    )

    return LaunchDescription([
        arg_robot_name,
        arg_enable_gz,
        joint_action_server_node,
        wheel_action_server_node,
        tts_node,
        stt_node,
        blockly_node,
    ])