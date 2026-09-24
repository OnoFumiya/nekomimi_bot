import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, OpaqueFunction, RegisterEventHandler
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch.event_handlers import OnProcessExit
from ament_index_python.packages import get_package_share_directory
from launch.conditions import IfCondition


def generate_launch_description():
    namespace_arg = DeclareLaunchArgument(
        "web_teleop_namespace",
        default_value="nekomimi_bot",
        description="Namespace for the nodes"
    )

    topic_name_arg = DeclareLaunchArgument(
        "web_teleop_topic_name",
        default_value="cmd_vel",
        description="Topic name for the teleoperation commands."
    )

    use_stamped_arg = DeclareLaunchArgument(
        "web_teleop_use_stamped",
        default_value="False",
        description="Whether to use stamped messages. (True: geometry_msgs/TwistStamped, False: geometry_msgs/Twist)"
    )

    websocket_port_arg = DeclareLaunchArgument(
        "web_teleop_websocket_port",
        default_value="7777",
        description="port number for network."
    )

    http_port_arg = DeclareLaunchArgument(
        "web_teleop_http_port",
        default_value="7000",
        description="port number for network server."
    )

    control_rate_arg = DeclareLaunchArgument(
        "control_rate",
        default_value="20",
        description="Velocity publish rate"
    )

    max_linear_arg = DeclareLaunchArgument(
        "max_linear_velocity",
        default_value="0.1",
        description="Max Velocity of foward linear.[m/s]"
    )

    max_angular_arg = DeclareLaunchArgument(
        "max_angular_velocity",
        default_value="0.65",
        description="Max Angular radian of rotation (angular).[rad/s]"
    )

    min_linear_arg = DeclareLaunchArgument(
        "min_linear_velocity",
        default_value="0.05",
        description="Max Velocity of foward linear.[m/s]"
    )

    min_angular_arg = DeclareLaunchArgument(
        "min_angular_velocity",
        default_value="0.08",
        description="Max Angular radian of rotation (angular).[rad/s]"
    )

    ui_bringup_arg = DeclareLaunchArgument(
        "web_teleop_ui_bringup",
        default_value="True",
        description="turn on the default engine for UI window (Blockly site)"
    )

    qrcode_view_arg = DeclareLaunchArgument(
        "web_teleop_qrcode_view",
        default_value="True",
        description="turn on the RQT Image View for QRcode.",
    )

    return LaunchDescription([
        namespace_arg,
        topic_name_arg,
        use_stamped_arg,
        websocket_port_arg,
        http_port_arg,
        control_rate_arg,
        max_linear_arg,
        max_angular_arg,
        min_linear_arg,
        min_angular_arg,
        ui_bringup_arg,
        qrcode_view_arg,
        OpaqueFunction(function = launch_nodes),
    ])


def launch_nodes(context, *args, **kwargs):

    pkg_share = get_package_share_directory("ros2_web_teleop")

    http_port = LaunchConfiguration('web_teleop_http_port').perform(context)
    websocket_port = LaunchConfiguration('web_teleop_websocket_port').perform(context)
    namespace = LaunchConfiguration('web_teleop_namespace').perform(context)

    if (http_port == websocket_port):
        print("\033[31mPlease use a different number. (http_port: " + http_port + ", websocket_port:" + websocket_port + ")\033[0m")
        return []

    replaced_cmd = ExecuteProcess(
        cmd=["sed", "-i", "5c const wsPort = " + str(websocket_port) + ";", pkg_share + "/web/js/websocket.js"],
    )

    display_server = ExecuteProcess(
        cmd=["python3", "-m", "http.server", http_port],
        cwd=os.path.join(pkg_share, "web"),
        output="screen",
    )

    delay_display_server = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=replaced_cmd,
            on_exit=[display_server],
        )
    )

    ros2_manager_node = Node(
        package="ros2_web_teleop",
        executable="teleop_node",
        name="web_teleop_manager",
        namespace=LaunchConfiguration('web_teleop_namespace'),
        output="screen",
        parameters=[
            {
                "topic_name": LaunchConfiguration("web_teleop_topic_name"),
                "use_stamped": LaunchConfiguration("web_teleop_use_stamped"),
                "websocket_port": LaunchConfiguration("web_teleop_websocket_port"),
                "http_port": LaunchConfiguration("web_teleop_http_port"),
                "control_rate": LaunchConfiguration("control_rate"),
                "max_linear_velocity": LaunchConfiguration("max_linear_velocity"),
                "max_angular_velocity": LaunchConfiguration("max_angular_velocity"),
                "min_linear_velocity": LaunchConfiguration("min_linear_velocity"),
                "min_angular_velocity": LaunchConfiguration("min_angular_velocity"),
                "ui_bringup": LaunchConfiguration("web_teleop_ui_bringup"),
            }
        ]
    )

    rqt_view_node = Node(
        namespace=LaunchConfiguration('web_teleop_namespace'),
        package="rqt_image_view",
        executable="rqt_image_view",
        name="qrcode_viewer",
        arguments=[("/" if (len(namespace) == 0) else ("/" + namespace + "/")) + "web_teleop_url_qrcode"],
        condition=IfCondition(LaunchConfiguration("web_teleop_qrcode_view")),
    )

    return [
        replaced_cmd,
        delay_display_server,
        ros2_manager_node,
        rqt_view_node,
    ]