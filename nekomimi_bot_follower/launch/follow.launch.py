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
            "config", "following_config.yaml"
        ),
    )

    execute_default_arg = DeclareLaunchArgument(
        "execute_default",
        description="Set to True to enable initialize detection",
        default_value="True",
    )

    namespace_arg = DeclareLaunchArgument(
        "namespace",
        description="Namespace (default: Empty)",
        default_value="nekomimi_bot",
    )

    param_file = LaunchConfiguration("param_file")
    execute_default = LaunchConfiguration("execute_default")
    namespace = LaunchConfiguration("namespace")


    dr_spaam_node_cmd = Node(
        package="dr_spaam_ros",
        executable="dr_spaam_ros",
        name="dr_spaam_ros",
        namespace=namespace,
        parameters=[param_file, {"execute_default": execute_default}],
        output="screen"
    )

    pantilt_follower_cmd = Node(
        package="nekomimi_bot_follower",
        executable="pantilt_follower",
        name="pantilt_follower",
        namespace=namespace,
        parameters=[param_file, {"execute_default": execute_default}],
        output="screen"
    )

    velocity_follower_cmd = Node(
        package="nekomimi_bot_follower",
        executable="velocity_follower",
        name="velocity_follower",
        namespace=namespace,
        parameters=[param_file, {"execute_default": execute_default}],
        output="screen"
    )


    return LaunchDescription([
        param_file_arg,
        execute_default_arg,
        namespace_arg,
        dr_spaam_node_cmd,
        pantilt_follower_cmd,
        # velocity_follower_cmd,
    ])
