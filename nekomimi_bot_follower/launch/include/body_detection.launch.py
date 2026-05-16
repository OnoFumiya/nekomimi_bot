
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription, LaunchContext
from launch.actions import DeclareLaunchArgument, OpaqueFunction, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node
from launch.conditions import IfCondition


def generate_launch_description():

    voc_object_prototxt_path = os.path.join(get_package_share_directory('ssd_ros'), 'models', 'voc_object.prototxt')
    voc_object_caffemodel_path = os.path.join(get_package_share_directory('ssd_ros'), 'models', 'voc_object.caffemodel')
    voc_object_names_path = os.path.join(get_package_share_directory('ssd_ros'), 'models', 'voc_object_names.txt')

    # 顔認識用
    # voc_object_prototxt_path = os.path.join(get_package_share_directory('ssd_ros'), 'models', 'face.prototxt')
    # voc_object_caffemodel_path = os.path.join(get_package_share_directory('ssd_ros'), 'models', 'face.caffemodel')
    # voc_object_names_path = os.path.join(get_package_share_directory('ssd_ros'), 'models', 'face_names.txt')

    params_file = LaunchConfiguration('params_file')
    params_file_arg = DeclareLaunchArgument(
        'params_file',
        default_value=os.path.join(get_package_share_directory('nekomimi_bot_follower'), 'config', 'ssd_config.yaml'),
        description='Full path to the ROS2 parameters file to use'
    )

    execute_default = LaunchConfiguration("execute_default")
    execute_default_cmd = DeclareLaunchArgument(
        "execute_default",
        description="Whether to start SSD enabled",
        default_value="true",
    )

    ssd_prototxt_name = LaunchConfiguration("ssd_prototxt_name")
    ssd_prototxt_name_cmd = DeclareLaunchArgument(
        "ssd_prototxt_name",
        description="ニューラルネットの構造を記述したtxt",
        default_value=voc_object_prototxt_path,
    )

    ssd_caffemodel_name = LaunchConfiguration("ssd_caffemodel_name")
    ssd_caffemodel_name_cmd = DeclareLaunchArgument(
        "ssd_caffemodel_name",
        description="学習済みモデル",
        default_value=voc_object_caffemodel_path,
    )

    ssd_class_names_file = LaunchConfiguration("ssd_class_names_file")
    ssd_class_names_file_cmd = DeclareLaunchArgument(
        "ssd_class_names_file",
        description="物体名リスト",
        default_value=voc_object_names_path,
    )

    ssd_ros_node_cmd = Node(
        package="ssd_ros",
        executable="single_shot_multibox_detector",
        name="ssd_ros",
        namespace="ssd_ros",
        parameters=[
            {
                "execute_default": execute_default,
                "ssd_prototxt_name": ssd_prototxt_name,
                "ssd_caffemodel_name": ssd_caffemodel_name,
                "ssd_class_names_file": ssd_class_names_file,
            },
            params_file,
        ],
        output="screen"
    )

    use_3d = LaunchConfiguration("use_3d")
    use_3d_cmd = DeclareLaunchArgument(
        "use_3d", default_value="true", description="Whether to activate 3D detections"
    )

    bbox_to_3d_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory("image_to_position"),
                "launch",
                "bbox_to_3d.launch.py",
            )
        ),
        launch_arguments={
            "namespace": "ssd_ros",
            "execute_default": execute_default,
            "params_file": params_file,
        }.items(),
        condition=IfCondition(use_3d),  # use_3dがTrueのときのみ実行
    )

    return LaunchDescription(
        [
            execute_default_cmd,
            params_file_arg,
            ssd_prototxt_name_cmd,
            ssd_caffemodel_name_cmd,
            ssd_class_names_file_cmd,
            ssd_ros_node_cmd,
            use_3d_cmd,
            bbox_to_3d_cmd,
        ]
    )
