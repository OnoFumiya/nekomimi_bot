from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, PythonExpression
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import ComposableNodeContainer, Node
from launch_ros.descriptions import ComposableNode
import yaml


def _load_detection_mode(params_path: str) -> str:
    detection_mode = "body_leg"
    try:
        with open(params_path, "r", encoding="utf-8") as f:
            params = yaml.safe_load(f) or {}
        detection_mode = params.get("/**", {}).get("ros__parameters", {}).get("detection_mode", detection_mode)
    except Exception:
        return detection_mode

    detection_mode = str(detection_mode).strip().lower()
    if detection_mode not in ("body", "leg", "body_leg"):
        detection_mode = "body_leg"
    return detection_mode


def _launch_setup(context):
    sobits_follower_share = FindPackageShare("sobits_follower")

    person_tracker_params = LaunchConfiguration("person_tracker_params")
    sensor_rotator_params = LaunchConfiguration("sensor_rotator_params")
    person_following_control_params = LaunchConfiguration("person_following_control_params")

    tracker_params_path = person_tracker_params.perform(context)
    detection_mode = _load_detection_mode(tracker_params_path)

    # DR-SPAAM launch includes
    dr_spaam_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare("nekomimi_bot_follower"),
                "launch",
                "include",
                "leg_detection.launch.py",
            ])
        ),
    )

    # SSD launch includes
    ssd_ros_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare("nekomimi_bot_follower"),
                "launch",
                "include",
                "body_detection.launch.py",
            ])
        ),
    )

    sobits_follower = ComposableNodeContainer(
        name="sobits_follower_container",
        namespace="sobits_follower",
        package="rclcpp_components",
        executable="component_container_mt",
        output="screen",
        composable_node_descriptions=[
            # Tracker Component
            ComposableNode(
                package="multiple_sensor_person_tracking",
                plugin="multiple_sensor_person_tracking::PersonTracker",
                name="person_tracker",
                namespace="",
                parameters=[person_tracker_params],
            ),
            # Sensor Rotator Component
            ComposableNode(
                package="multiple_sensor_person_tracking",
                plugin="multiple_sensor_person_tracking::PersonAimSensorRotator",
                name="person_aim_sensor_rotator",
                namespace="",
                parameters=[sensor_rotator_params],
            ),
            # Following Control Component
            ComposableNode(
                package="person_following_control",
                plugin="person_following_control::PersonFollowing",
                name="person_following_control",
                namespace="",
                parameters=[person_following_control_params],
            ),
        ],
    )

    actions = []
    if detection_mode != "body":
        actions.append(dr_spaam_launch)
    if detection_mode != "leg":
        actions.append(ssd_ros_launch)
    actions.append(sobits_follower)
    return actions

def generate_launch_description():


    launch_args = [
        DeclareLaunchArgument(
            "person_tracker_params", 
            description="Path to the person tracker parameter file",
            default_value=PathJoinSubstitution([
                FindPackageShare("nekomimi_bot_follower"), 
                "config",
                "tracker_param.yaml"
            ])
        ),
        DeclareLaunchArgument(
            "sensor_rotator_params", 
            description="Path to the sensor rotator parameter file",
            default_value=PathJoinSubstitution([
                FindPackageShare("nekomimi_bot_follower"), 
                "config", 
                "sensor_rotator_param.yaml"
            ])
        ),
        DeclareLaunchArgument(
            "person_following_control_params", 
            description="Path to the person following control parameter file",
            default_value=PathJoinSubstitution([
                FindPackageShare("nekomimi_bot_follower"), 
                "config",
                "following_control_param.yaml"
            ])
        ),
    ]
    return LaunchDescription(launch_args + [OpaqueFunction(function=_launch_setup)])
