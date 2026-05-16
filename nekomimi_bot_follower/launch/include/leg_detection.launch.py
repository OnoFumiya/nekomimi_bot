import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    param_file_arg = DeclareLaunchArgument(
        "param_file",
        description="yaml file path for config file (dr spaam ros etc...)",
        default_value=os.path.join(
            get_package_share_directory("nekomimi_bot_follower"),
            "config", "dr_spaam_config.yaml"
        ),
    )

    execute_default_arg = DeclareLaunchArgument(
        "execute_default",
        description="Set to True to enable initialize detection",
        default_value="True",
    )

    param_file = LaunchConfiguration("param_file")
    execute_default = LaunchConfiguration("execute_default")
    namespace = LaunchConfiguration("namespace")


    dr_spaam_node_cmd = Node(
        package="dr_spaam_ros",
        executable="dr_spaam_ros",
        name="dr_spaam_ros",
        namespace="nekomimi_bot",
        parameters=[param_file, {"execute_default": execute_default}],
        output="screen"
    )


    return LaunchDescription([
        param_file_arg,
        execute_default_arg,
        dr_spaam_node_cmd,
    ])
