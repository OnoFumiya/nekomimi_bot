from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
import os

def generate_launch_description():
    stt_name_arg = DeclareLaunchArgument(
        "stt_name",
        default_value="vosk",
        description="STT engine name (whisper, vosk, etc.)"
    )

    model_arg = DeclareLaunchArgument(
        "model",
        default_value="vosk-model-ja-0.22",
        description="Vosk model name"
    )
    mic_volume_arg = DeclareLaunchArgument(
        "mic_volume",
        default_value="",
        description="Microphone volume percentage"
    )
    use_echo_cancel_arg = DeclareLaunchArgument(
        "use_echo_cancel",
        default_value="False",
        description="Enable WebRTC echo cancellation"
    )
    noise_suppression_arg = DeclareLaunchArgument(
        "noise_suppression",
        default_value="False",
        description="Enable noise suppression"
    )
    analog_gain_arg = DeclareLaunchArgument(
        "analog_gain_control",
        default_value="False",
        description="Enable automatic analog gain control"
    )
    digital_gain_arg = DeclareLaunchArgument(
        "digital_gain_control",
        default_value="False",
        description="Enable digital gain control"
    )
    use_feedback_arg = DeclareLaunchArgument(
        "use_feedback",
        default_value="True",
        description="Enable intermediate streaming feedback"
    )
    vosk_grammar_arg = DeclareLaunchArgument(
        "vosk_grammar",
        default_value="",
        description="JSON grammar string for Vosk recognizer (empty = no grammar)"
    )
    namespace_arg = DeclareLaunchArgument(
        "namespace",
        default_value="nekomimi_bot",
        description="Namespace for the nodes"
    )

    vosk_node = Node(
        package='sobits_speech_recognition',
        executable='stt_server',
        name='stt_server',
        namespace=LaunchConfiguration('namespace'),
        output='screen',
        parameters=[{
            'stt_name': LaunchConfiguration('stt_name'),
            'model': LaunchConfiguration('model'),
            'mic_volume': LaunchConfiguration('mic_volume'),
            'use_echo_cancel': LaunchConfiguration('use_echo_cancel'),
            'noise_suppression': LaunchConfiguration('noise_suppression'),
            'analog_gain_control': LaunchConfiguration('analog_gain_control'),
            'digital_gain_control': LaunchConfiguration('digital_gain_control'),
            'use_feedback': LaunchConfiguration('use_feedback'),
            'vosk_grammar': LaunchConfiguration('vosk_grammar'),
        }],
    )

    return LaunchDescription([
        namespace_arg,
        stt_name_arg,
        model_arg,
        mic_volume_arg,
        use_echo_cancel_arg,
        noise_suppression_arg,
        analog_gain_arg,
        digital_gain_arg,
        use_feedback_arg,
        vosk_grammar_arg,
        vosk_node
    ])