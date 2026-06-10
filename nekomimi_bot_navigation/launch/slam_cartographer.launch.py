
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (DeclareLaunchArgument, EmitEvent, LogInfo,
                            RegisterEventHandler, OpaqueFunction)
from launch.conditions import IfCondition
from launch.events import matches_action
from launch.substitutions import (LaunchConfiguration, PathJoinSubstitution,
                                  TextSubstitution)
from launch_ros.actions import LifecycleNode, Node
from launch_ros.event_handlers import OnStateTransition
from launch_ros.events.lifecycle import ChangeState
from lifecycle_msgs.msg import Transition



def generate_launch_description():
    ########## Customizable parameters ##########
    declare_save_map_command_cmd = DeclareLaunchArgument(
        'save_map_command', default_value='true',
        description='command map saver select')

    declare_rviz_viewer_cmd = DeclareLaunchArgument(
        'rviz_viewer', default_value='true',
        description='use rviz')

    declare_use_sim_time_argument = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='Use simulation/Gazebo clock')
    #############################################

    cartographer_config_dir = PathJoinSubstitution([os.path.join(get_package_share_directory("nekomimi_bot_navigation"), 'config')])
    cartographer_config_basename = TextSubstitution(text='slam.lua')

    save_map_command = LaunchConfiguration('save_map_command')
    rviz_viewer = LaunchConfiguration('rviz_viewer')
    use_sim_time = LaunchConfiguration('use_sim_time')

    cartographer_node = Node(
        package='cartographer_ros',
        executable='cartographer_node',
        name='cartographer_node',
        output='screen',
        parameters=[
            {'use_sim_time': use_sim_time}
        ],
        arguments=[
            '-configuration_directory', cartographer_config_dir,
            '-configuration_basename', cartographer_config_basename
        ],
        remappings=[('/scan', '/nekomimi_bot/scan'), ('/odom', '/nekomimi_bot/odom')]
    )

    cartographer_occupancy_grid_node = Node(
        package='cartographer_ros',
        executable='cartographer_occupancy_grid_node',
        parameters=[
            {'use_sim_time': use_sim_time},
            {'-resolution': '0.05'},
            {'-publish_period_sec': '1.0'}
        ],
    )

    map_saver_gui = Node(
        package='nekomimi_bot_navigation',
        executable='map_saver_gui.py',
        name='map_saver_gui',
        output='log',
        parameters=[{'use_sim_time': use_sim_time}],
        condition=IfCondition(save_map_command),
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        output='log',
        arguments=['-d', os.path.join(get_package_share_directory("nekomimi_bot_navigation"), 'rviz', 'navigation.rviz')],
        condition=IfCondition(rviz_viewer),
    )

    ld = LaunchDescription()

    ld.add_action(declare_save_map_command_cmd)
    ld.add_action(declare_rviz_viewer_cmd)
    ld.add_action(declare_use_sim_time_argument)
    ld.add_action(cartographer_node)
    ld.add_action(cartographer_occupancy_grid_node)
    ld.add_action(map_saver_gui)
    ld.add_action(rviz_node)

    return ld