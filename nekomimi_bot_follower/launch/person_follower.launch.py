from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, PythonExpression
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import ComposableNodeContainer, Node
from launch_ros.descriptions import ComposableNode
import yaml


def _load_ros_parameters(params_path: str) -> dict:
    try:
        with open(params_path, "r", encoding="utf-8") as f:
            params = yaml.safe_load(f) or {}
    except Exception:
        return {}

    return params.get("/**", {}).get("ros__parameters", {}) or {}


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
    person_follower_share = FindPackageShare("person_follower")

    person_tracker_params = LaunchConfiguration("person_tracker_params")
    sensor_rotator_params = LaunchConfiguration("sensor_rotator_params")
    person_following_control_params = LaunchConfiguration("person_following_control_params")
    velocity_smoother_params = LaunchConfiguration("velocity_smoother_params")

    tracker_params_path = person_tracker_params.perform(context)
    detection_mode = _load_detection_mode(tracker_params_path)

    velocity_smoother_config = _load_ros_parameters(velocity_smoother_params.perform(context))
    raw_cmd_vel_topic = str(velocity_smoother_config.get("raw_cmd_vel_topic", "person_follower/velocity_smoother/raw_cmd_vel")).strip()
    output_cmd_vel_topic = str(velocity_smoother_config.get("output_cmd_vel_topic", "/cmd_vel")).strip()
    person_following_control_overrides = {
        "command_velocity_topic_name": raw_cmd_vel_topic,
        "stop_command_velocity_topic_name": output_cmd_vel_topic
    }

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

    velocity_smoother_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare("person_following_control"),
                "launch",
                "velocity_smoother.launch.py",
            ])
        ),
        launch_arguments={
            "use_velocity_smoother": "true",
            "velocity_smoother_params": velocity_smoother_params,
            "autostart_lifecycle": "true",
        }.items(),
    )

    person_follower = ComposableNodeContainer(
        name="person_follower_container",
        namespace="",
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
                parameters=[person_following_control_params, person_following_control_overrides],
            ),
        ],
    )

    lifecycle_manager = Node(
        package="nav2_lifecycle_manager",
        executable="lifecycle_manager",
        name="person_follower_lifecycle_manager",
        namespace="",
        output="screen",
        parameters=[{
            "autostart": True,
            "bond_timeout": 0.0,
            "node_names": [
                "person_tracker",
                "person_aim_sensor_rotator",
                "person_following_control",
            ],
        }],
    )

    actions = []
    # if detection_mode != "body":
    #     actions.append(dr_spaam_launch)
    # if detection_mode != "leg":
    #     actions.append(ssd_ros_launch)
    actions.append(person_follower)
    actions.append(lifecycle_manager)
    actions.append(velocity_smoother_launch)
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
        DeclareLaunchArgument(
            "velocity_smoother_params", 
            description="Path to the velocity smoother parameter file",
            default_value=PathJoinSubstitution([
                FindPackageShare("nekomimi_bot_follower"), 
                "config",
                "velocity_smoother_param.yaml"
            ])
        ),
    ]
    return LaunchDescription(launch_args + [OpaqueFunction(function=_launch_setup)])
