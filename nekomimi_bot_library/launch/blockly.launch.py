import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from launch.conditions import IfCondition
# from launch.actions import ExecuteProcess, OpaqueFunction, RegisterEventHandler, IncludeLaunchDescription


def generate_launch_description():
    pkg_share = get_package_share_directory("nekomimi_bot_library")

    default_config_file = os.path.join(pkg_share, "config", "nekomimi_blockly.yaml")

    namespace_arg = DeclareLaunchArgument(
        "blockly_namespace",
        default_value="nekomimi_bot",
        description="Namespace for the nodes"
    )

    block_config_arg = DeclareLaunchArgument(
        "block_config",
        default_value=default_config_file,
        description="Custom Block to use Blockly structure config file"
    )

    ui_bringup_arg = DeclareLaunchArgument(
        "ui_bringup",
        default_value="False",
        description="turn on the default engine for UI window (Blockly site)"
    )

    qrcode_view_arg = DeclareLaunchArgument(
        "qrcode_view",
        default_value="False",
        description="turn on the RQT Image View for QRcode.",
    )

    return LaunchDescription([
        namespace_arg,
        block_config_arg,
        ui_bringup_arg,
        qrcode_view_arg,
        OpaqueFunction(function = node_bringup),
    ])


def node_bringup(context, *args, **kwargs):
    blockly_namespace = LaunchConfiguration('blockly_namespace').perform(context)

    ros2_manager_node = Node(
        package="blockly_ros2",
        executable="server",
        name="blockly_ros2_node",
        namespace=blockly_namespace,
        output="screen",
        parameters=[
            {
                "block_config": LaunchConfiguration("block_config"),
                "port": 5000,
                "ui_bringup": LaunchConfiguration("ui_bringup"),
            }
        ]
    )

    rqt_view_node = Node(
        package="rqt_image_view",
        executable="rqt_image_view",
        name="qrcode_viewer",
        arguments=[blockly_namespace + "/blockly_url_qrcode"],
        condition=IfCondition(LaunchConfiguration("qrcode_view")),
    )

    return [
        ros2_manager_node,
        rqt_view_node,
    ]
