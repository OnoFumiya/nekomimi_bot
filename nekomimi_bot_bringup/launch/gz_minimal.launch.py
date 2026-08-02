import os

from ament_index_python.packages import get_package_share_directory

from launch_ros.actions import Node

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution


def generate_launch_description():
    robot_name = 'nekomimi_bot'
    robot_id = 0
    bringup_pkg = robot_name + '_bringup'

    # world_model = 'empty'
    # world_model = 'wrs'
    # world_model = 'small_house'
    world_model = 'multi_floor_cafeteria' # 'rcjo2025_arena'

    rviz_config = os.path.join(get_package_share_directory(bringup_pkg), 'rviz', 'gazebo.rviz')

    world_file = ''
    if world_model == 'empty':
        world_file = os.path.join(get_package_share_directory(
            'nekomimi_bot_description'), 
            'worlds',
            'empty.sdf'
        )
        starting_pose = {"x": 0.0, "y": 0.0, "z": 0.0, "yaw": 0.0}
    elif world_model == 'wrs':
        world_file = os.path.join(get_package_share_directory(
            'tmc_wrs_gz_worlds'), 
            'worlds',
            'wrs2020.world.xacro'
        )
        starting_pose = {"x": 0.0, "y": 0.0, "z": 0.0, "yaw": 0.0}
    elif world_model == 'small_house':
        world_file = os.path.join(get_package_share_directory(
            'aws_small_house_world'), 
            'worlds',
            'small_house.world'
        )
        starting_pose = {"x": 0.0, "y": 0.0, "z": 0.0, "yaw": 0.0}
    else:
        world_file = os.path.join(get_package_share_directory(
            'gazebo_worlds'), 
            'worlds',
            world_model + '.world.xacro'
        )
        if world_model == 'rcjo2025_arena':
            starting_pose = {"x": -5.5, "y": 1.5, "z": 0.0, "yaw": 3.14}
        elif world_model == 'multi_floor_cafeteria':
            starting_pose = {"x": -0.5, "y": 4.375, "z": 0.0, "yaw": 3.14}
            # starting_pose = {"x": -0.5, "y": 4.375, "z": 3.0, "yaw": 3.14}



    return LaunchDescription([
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                PathJoinSubstitution([
                    os.path.join(get_package_share_directory('ros_gz_sim'),
                    'launch',
                    'gz_sim.launch.py')
                ])
            ]),
            launch_arguments={
                'gz_args' : ' -r -v 4 ' + world_file,
            }.items()
        ),

        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            arguments=[
                        "/clock" + "@rosgraph_msgs/msg/Clock" + "[ignition.msgs.Clock",
                        "/tf" + "@tf2_msgs/msg/TFMessage" + "[ignition.msgs.Pose_V",
                    ],
        ),

        # Launch Robot No. 1
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                PathJoinSubstitution([
                    os.path.join(get_package_share_directory(bringup_pkg),
                    'launch',
                    'robot.launch.py')
                ])
            ]),
            launch_arguments={
                'robot_name': robot_name if robot_id == 0 else robot_name + '_' + str(robot_id),
                'enable_gz' : 'True',
                'enable_gz_lidar' : 'True',

                # Empty World
                'robot_coords_x': str(starting_pose["x"]),   # x
                'robot_coords_y': str(starting_pose["y"]),   # y
                'robot_coords_z': str(starting_pose["z"]),   # z
                'robot_coords_Y': str(starting_pose["yaw"]), # yaw
            }.items()
        ),

        Node(
            package='rviz2',
            executable='rviz2',
            namespace=robot_name,
            name='rviz2',
            arguments=['-d', rviz_config],
            output='screen',
        ),
    ])
