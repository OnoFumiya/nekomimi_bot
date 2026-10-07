import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from launch.conditions import IfCondition


def generate_launch_description():

    namespace_arg = DeclareLaunchArgument(
        "web_gui_namespace",
        default_value="nekomimi_bot",
        description="Namespace for the nodes"
    )

    qrcode_view_arg = DeclareLaunchArgument(
        "qrcode_view",
        default_value="False",
        description="turn on the RQT Image View for QRcode.",
    )

    ros2_manager_node = Node(
        package="ros2_web_gui_portal",
        executable="portal_node",
        name="ros2_web_gui_node",
        namespace=LaunchConfiguration('web_gui_namespace'),
        output="screen",
        parameters=[
            {
                "browser_name": "Nekomimi Bot GUI",
                "web_portal_config_file": os.path.join(get_package_share_directory("nekomimi_bot_library"), "config", "library_gui_settings.yaml"),
                "web_portal_port": 9000,
                "wait_for_subscribers": True,
                "ui_bringup": False,
            }
        ]
    )


    return LaunchDescription([
        namespace_arg,
        qrcode_view_arg,
        ros2_manager_node,
        OpaqueFunction(function = rqt_view_node_bringup),
    ])


def rqt_view_node_bringup(context, *args, **kwargs):

    namespace = LaunchConfiguration('web_gui_namespace').perform(context)

    rqt_view_node = Node(
        namespace=LaunchConfiguration('web_gui_namespace'),
        package="rqt_image_view",
        executable="rqt_image_view",
        name="qrcode_viewer",
        arguments=[("/" if (len(namespace) == 0) else ("/" + namespace + "/")) + "portal_url_qrcode"],
        condition=IfCondition(LaunchConfiguration("qrcode_view")),
    )

    return [rqt_view_node]