#include <iostream>
#include <random>
#include <string>
#include <cstdio>
#include <memory>
#include <stdexcept>
#include <regex>

#include <std_msgs/msg/bool.hpp>
#include <std_msgs/msg/float64_multi_array.hpp>
#include <sensor_msgs/msg/joint_state.hpp>
#include <sensor_msgs/msg/battery_state.hpp>
#include <geometry_msgs/msg/twist.hpp>
#include <nav_msgs/msg/odometry.hpp>

#include <control_msgs/action/follow_joint_trajectory.hpp>

#include <rclcpp/rclcpp.hpp>
#include <rclcpp_components/register_node_macro.hpp>
// #include <ament_index_cpp/get_package_share_directory.hpp> // (C++18)
#include <ament_index_cpp/get_package_share_path.hpp>      // (C++20)

#include "nekomimi_bot_bringup/nekomimi_bot_wheel_control.hpp"
#include "nekomimi_bot_bringup/nekomimi_bot_wheel_odometry.hpp"

namespace nekomimi_bot
{
class NekomimiBotWheelController : public rclcpp::Node
{
public:
  explicit NekomimiBotWheelController(const rclcpp::NodeOptions & options);
  ~NekomimiBotWheelController();

  void sound_play(std::string sound_name);

private:    
  // ROS2 I/F
  rclcpp::Subscription<geometry_msgs::msg::Twist>::SharedPtr     sub_vel_;
  rclcpp::Subscription<sensor_msgs::msg::JointState>::SharedPtr  sub_joint_info_;

  rclcpp::Publisher<nav_msgs::msg::Odometry>::SharedPtr          pub_odometry_;
  rclcpp::Publisher<std_msgs::msg::Float64MultiArray>::SharedPtr pub_body_roll_vel_;
  rclcpp::Publisher<std_msgs::msg::Float64MultiArray>::SharedPtr pub_wheel_vel_;
  rclcpp::Publisher<sensor_msgs::msg::BatteryState>::SharedPtr   pub_battery_;

  // Control & Sensing Callbacks
  void joint_callback(const sensor_msgs::msg::JointState::SharedPtr msg);
  void control_callback();

  // Control Variables
  std_msgs::msg::Float64MultiArray body_roll_joint_vel;
  std_msgs::msg::Float64MultiArray wheel_joint_vel;

  // Battery Info
  sensor_msgs::msg::BatteryState battery_value;

  std::map<std::string, double> joints_pos;

  std::unique_ptr<NekomimiBotWheelControl>  nekomimi_bot_wheel_control_;
  std::unique_ptr<NekomimiBotWheelOdometry> nekomimi_bot_wheel_odometry_;

  rclcpp::TimerBase::SharedPtr control_timer_;

  std::string body_roll_joint_name;
  std::vector<std::string> drive_joints_names;
};
} // namespace nekomimi_bot

RCLCPP_COMPONENTS_REGISTER_NODE(nekomimi_bot::NekomimiBotWheelController)