import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch.conditions import IfCondition

def generate_launch_description():
    ########## Customizable parameters ##########
    declare_save_map_command_cmd = DeclareLaunchArgument(
        'save_map_command', default_value='true',
        description='command map saver select')

    declare_robot_base_frame_cmd = DeclareLaunchArgument(
        'robot_base_frame', default_value='nekomimi_bot/lidar_link',
        description='robot base frame name')

    declare_custom_costmap_layer_cmd = DeclareLaunchArgument(
        'custom_costmap_layer', default_value='scan',
        description='custom costmap layer type (e.g., "scan", "scan rgbd")')
    #############################################

    # Get the launch directory
    navigation_dir = get_package_share_directory('nekomimi_bot_navigation')

    explore_config = os.path.join(get_package_share_directory("explore_lite"), "config", "params.yaml")

    save_map_command = LaunchConfiguration('save_map_command')
    robot_base_frame = LaunchConfiguration('robot_base_frame')
    use_sim_time = LaunchConfiguration('use_sim_time')
    custom_costmap_layer = LaunchConfiguration('custom_costmap_layer')

    use_sim_time_cmd = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='Use simulation (Gazebo) clock if true')

    nav2_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(navigation_dir, "launch", "navigation.launch.py")),
        launch_arguments={
                            "use_sim_time": use_sim_time,
                            'slam': "True",
                            'location': "",
                            'use_rviz': 'False',
                            'use_keepout_map': 'False',
                            'custom_costmap_layer': custom_costmap_layer,
                        }.items())

    explore_node_cmd = Node(
        package="explore_lite",
        name="explore_node",
        executable="explore",
        parameters=[explore_config, 
                    {
                        "robot_base_frame": robot_base_frame,
                        "return_to_init": "False",
                        "use_sim_time": use_sim_time,
                        "progress_timeout": "90.0"
                    }],
        output="screen",
        remappings=[("/tf", "tf"), ("/tf_static", "tf_static")],
    )

    map_saver_gui = Node(
        package='nekomimi_bot_navigation',
        executable='map_saver_gui.py',
        name='map_saver_gui',
        output='log',
        parameters=[{'use_sim_time': use_sim_time}],
        condition=IfCondition(save_map_command),
    )

    rviz_cmd = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', os.path.join(navigation_dir, 'rviz', 'navigation.rviz')]
    )

    # Create the launch description and populate
    ld = LaunchDescription()

    # ld.add_action(declare_robot_name_cmd)
    ld.add_action(declare_save_map_command_cmd)
    ld.add_action(use_sim_time_cmd)
    ld.add_action(declare_robot_base_frame_cmd)
    ld.add_action(declare_custom_costmap_layer_cmd)
    ld.add_action(nav2_cmd)
    ld.add_action(explore_node_cmd)
    ld.add_action(map_saver_gui)
    ld.add_action(rviz_cmd)

    return ld
