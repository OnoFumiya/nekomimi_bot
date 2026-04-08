import os
from ament_index_python.packages import get_package_share_directory

from launch_ros.actions import Node

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, OpaqueFunction, RegisterEventHandler, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch.event_handlers import OnProcessExit

import xacro


def generate_launch_description():
    arg_robot_name = DeclareLaunchArgument('robot_name', default_value='nekomimi_bot')

    arg_robot_coords_x = DeclareLaunchArgument('robot_coords_x', default_value='0')
    arg_robot_coords_y = DeclareLaunchArgument('robot_coords_y', default_value='0')
    arg_robot_coords_z = DeclareLaunchArgument('robot_coords_z', default_value='0')
    arg_robot_coords_Y = DeclareLaunchArgument('robot_coords_Y', default_value='0')

    arg_enable_gz   = DeclareLaunchArgument('enable_gz'  , default_value='False')

    arg_enable_gz_lidar = DeclareLaunchArgument('enable_gz_lidar', default_value='True')

    return LaunchDescription([
        arg_robot_name,
        arg_robot_coords_x,
        arg_robot_coords_y,
        arg_robot_coords_z,
        arg_robot_coords_Y,
        arg_enable_gz,
        arg_enable_gz_lidar,
        OpaqueFunction(function = launch_gz),
    ])


def launch_gz(context, *args, **kwargs):
    robot_name = LaunchConfiguration('robot_name').perform(context)

    robot_coords_x = LaunchConfiguration('robot_coords_x').perform(context)
    robot_coords_y = LaunchConfiguration('robot_coords_y').perform(context)
    robot_coords_z = LaunchConfiguration('robot_coords_z').perform(context)
    robot_coords_Y = LaunchConfiguration('robot_coords_Y').perform(context)

    enable_gz = LaunchConfiguration('enable_gz').perform(context)

    enable_gz_lidar = LaunchConfiguration('enable_gz_lidar').perform(context)

    ftc_sl_port = ''
    lds_sl_port = ''
    if enable_gz == 'False':
        ftc_sl_port = str(os.environ.get('FTC_SL_PORT'))
        print('Feetech Serial Port : ' + ftc_sl_port)
        lds_sl_port = str(os.environ.get('LDS_SL_PORT'))
        print('HLDS Serial Port : ' + lds_sl_port)

    robot_description = os.path.join(get_package_share_directory(
        'nekomimi_bot_description'), 
        'robots',
        'nekomimi_bot_robot.urdf.xacro'
    )

    wheel_controller_config = os.path.join(get_package_share_directory(
        'nekomimi_bot_bringup'), 
        'config',
        'wheel_controller.yaml'
    )

    robot_description_config = xacro.process_file(
        robot_description,
        mappings={
            'enable_gz'      : enable_gz,
            'robot_name'     : robot_name,
            'enable_gz_lidar': enable_gz_lidar,
            'ftc_sl_port'    : ftc_sl_port,
        })

    if enable_gz == 'False':
        controller_config = os.path.join(get_package_share_directory(
            'nekomimi_bot_bringup'),
            'config',
            'controllers.yaml'
        )

        controller_manager = Node(
            package="controller_manager",
            executable="ros2_control_node",
            namespace=robot_name,
            parameters=[
                {"robot_description": robot_description_config.toxml()}, controller_config],
            output="screen",
        )

        lidar_node = IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                PathJoinSubstitution([
                    FindPackageShare('hls_lfcd_lds_driver'),
                    'launch',
                    'hlds_laser.launch.py'
                ])
            ]),
            launch_arguments={
                'port': lds_sl_port,
                'namespace': robot_name,
                'frame_id' : 'lidar_link',
                'angle_min': '-1.57',
                'angle_max':  '1.57',
            }.items(),
        )

    joint_state_broadcaster = Node(
        package='controller_manager',
        executable='spawner',
        # name='joint_state_broadcaster',
        namespace=robot_name,
        arguments=[
            'joint_state_broadcaster',
            '-c', 'controller_manager',
        ],
    )

    joint_trajectory_controller = Node(
        package='controller_manager',
        executable='spawner',
        # name='joint_trajectory_controller',
        namespace=robot_name,
        arguments=[
            'joint_trajectory_controller',
            '-c', 'controller_manager', '--activate'
        ],
    )

    mobile_base_position_controller = Node(
        package='controller_manager',
        executable='spawner',
        # name='mobile_base_position_controller',
        namespace=robot_name,
        arguments=[
            'mobile_base_position_controller',
            '-c', 'controller_manager', '--activate'
        ],
    )

    velocity_controller = Node(
        package='controller_manager',
        executable='spawner',
        # name='velocity_controller',
        namespace=robot_name,
        arguments=[
            'velocity_controller',
            '-c', 'controller_manager', '--activate'
        ],
    )

    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        namespace=robot_name,
        parameters=[
            {"frame_prefix": robot_name + '/'},
            {"robot_description": robot_description_config.toxml()},
            {"use_sim_time": True if enable_gz == 'True' else False},
        ],
        output="screen",
    )

    library_server_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('nekomimi_bot_library'),
                'launch',
                'library_server.launch.py'
            ])
        ]),
        launch_arguments={
            'robot_name': robot_name,
            'enable_gz': enable_gz,
        }.items(),
    )

    move_base_node = Node(
        package="nekomimi_bot_bringup",
        executable="nekomimi_bot_wheel_node",
        name="wheel_controller",
        namespace=robot_name,
        parameters=[
            wheel_controller_config,
            {"use_sim_time": True if enable_gz == 'True' else False},
        ],
        output="screen",
    )

    if enable_gz == 'True':
        gz_spawn_entity_node = Node(
            package='ros_gz_sim',
            executable='create',
            namespace=robot_name,
            arguments=[
                '-topic', '/' + robot_name + '/robot_description',
                '-name', robot_name,
                '-x', robot_coords_x,
                '-y', robot_coords_y,
                '-z', robot_coords_z,
                '-Y', robot_coords_Y,
            ],
            output='screen',
        )

        gz_bridge_node = Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            namespace=robot_name,
            arguments=[
                        "/" + robot_name + "/joint_states" + "@sensor_msgs/msg/JointState" + "[ignition.msgs.Model",
                        # "/" + robot_name + "/hand_camera/depth" + "@sensor_msgs/msg/Image" + "[ignition.msgs.Image",
                        # "/" + robot_name + "/hand_camera/depth/points" + "@sensor_msgs/msg/PointCloud2" + "[ignition.msgs.PointCloudPacked",
                        "/" + robot_name + "/scan" + "@sensor_msgs/msg/LaserScan" + "[ignition.msgs.LaserScan",
                        # "/" + robot_name + "/imu" + "@sensor_msgs/msg/Imu" + "[ignition.msgs.IMU",
                    ],
            output='screen'
        )

    if enable_gz == 'False':
        return [
            controller_manager,
            joint_state_broadcaster,
            joint_trajectory_controller,
            mobile_base_position_controller,
            velocity_controller,
            robot_state_publisher_node,
            lidar_node,
            RegisterEventHandler(
                event_handler=OnProcessExit(
                    target_action=joint_state_broadcaster,
                    on_exit=[move_base_node],
                )
            ),
            RegisterEventHandler(
                event_handler=OnProcessExit(
                    target_action=joint_state_broadcaster,
                    on_exit=[library_server_launch],
                )
            ),
        ]

    else:
        return [
            gz_spawn_entity_node,
            gz_bridge_node,
            RegisterEventHandler(
                event_handler=OnProcessExit(
                    target_action=gz_spawn_entity_node,
                    on_exit=[joint_state_broadcaster],
                )
            ),
            RegisterEventHandler(
                event_handler=OnProcessExit(
                    target_action=joint_state_broadcaster,
                    on_exit=[joint_trajectory_controller],
                )
            ),
            RegisterEventHandler(
                event_handler=OnProcessExit(
                    target_action=joint_state_broadcaster,
                    on_exit=[mobile_base_position_controller],
                )
            ),
            RegisterEventHandler(
                event_handler=OnProcessExit(
                    target_action=joint_state_broadcaster,
                    on_exit=[velocity_controller],
                )
            ),
            RegisterEventHandler(
                event_handler=OnProcessExit(
                    target_action=joint_state_broadcaster,
                    on_exit=[move_base_node],
                )
            ),
            RegisterEventHandler(
                event_handler=OnProcessExit(
                    target_action=joint_state_broadcaster,
                    on_exit=[library_server_launch],
                )
            ),
            robot_state_publisher_node,
        ]
