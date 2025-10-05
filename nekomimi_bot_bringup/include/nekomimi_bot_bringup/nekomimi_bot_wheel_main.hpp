#include <iostream>
#include <random>

#include <std_msgs/msg/bool.hpp>
#include <std_msgs/msg/float64_multi_array.hpp>
#include <sensor_msgs/msg/joint_state.hpp>
#include <geometry_msgs/msg/twist.hpp>
#include <trajectory_msgs/msg/joint_trajectory.hpp>
#include <nav_msgs/msg/odometry.hpp>

#include <control_msgs/action/follow_joint_trajectory.hpp>

#include <rclcpp/rclcpp.hpp>
#include <rclcpp_components/register_node_macro.hpp>
#include <ament_index_cpp/get_package_share_directory.hpp>

#include "nekomimi_bot_bringup/nekomimi_bot_wheel_control.hpp"
#include "nekomimi_bot_bringup/nekomimi_bot_wheel_odometry.hpp"

namespace nekomimi_bot
{
class NekomimiBotWheelMain : public rclcpp::Node
{
public:
  explicit NekomimiBotWheelMain(const rclcpp::NodeOptions & options);
  ~NekomimiBotWheelMain();

  void sound_play(std::string sound_name);

private:    
  // ROS2 I/F
  rclcpp::Subscription<geometry_msgs::msg::Twist>::SharedPtr    sub_vel_;
  rclcpp::Subscription<sensor_msgs::msg::JointState>::SharedPtr sub_joint_info_;

  rclcpp::Publisher<nav_msgs::msg::Odometry>::SharedPtr               pub_odometry_;
  rclcpp::Publisher<trajectory_msgs::msg::JointTrajectory>::SharedPtr pub_body_roll_joint_;
  rclcpp::Publisher<std_msgs::msg::Float64MultiArray>::SharedPtr      pub_wheel_vel_;

  // Control & Sensing Callbacks
  void vel_callback(const geometry_msgs::msg::Twist::SharedPtr msg);
  void joint_callback(const sensor_msgs::msg::JointState::SharedPtr msg);
  void controller();

  // Publishing Helpers
  void setPosJointTrajectory(const std::string& joint_name, double rad, double sec, trajectory_msgs::msg::JointTrajectory* jt);

  // Control Variables
  trajectory_msgs::msg::JointTrajectory body_roll_joint_trajectory;
  std_msgs::msg::Float64MultiArray      wheel_joint_vel;

  // order twist
  geometry_msgs::msg::Twist vel_twist_;
  bool is_twist_callback_;

  // 
  std::map<std::string, double> joints_pos;
  std::map<std::string, double> wheels_prev_pos;
  std::map<std::string, double> wheels_curt_pos;


  // Desired (target) steering positions and wheel velocities
  std::array<double, 3> set_wheels_vel;
  std::array<double, 3> prev_wheels_vel;

  nav_msgs::msg::Odometry result_odom;
  nav_msgs::msg::Odometry prev_odom;

  std::unique_ptr<NekomimiBotWheelControl>  nekomimi_bot_wheel_control_;
  std::unique_ptr<NekomimiBotWheelOdometry> nekomimi_bot_wheel_odometry_;

  rclcpp::TimerBase::SharedPtr control_timer_;

  std::string robot_name; // topic name space
};

inline void NekomimiBotWheelMain::setPosJointTrajectory(
  const std::string& joint_name,
  double rad, double sec,
  trajectory_msgs::msg::JointTrajectory* jt)
{
  trajectory_msgs::msg::JointTrajectory      joint_trajectory;
  trajectory_msgs::msg::JointTrajectoryPoint joint_trajectory_point;

  joint_trajectory.joint_names.push_back( joint_name );
  joint_trajectory_point.positions.push_back( rad );
  joint_trajectory_point.time_from_start = rclcpp::Duration::from_seconds(sec);
  joint_trajectory.points.push_back( joint_trajectory_point );

  *jt = joint_trajectory;
}

} // namespace nekomimi_bot

RCLCPP_COMPONENTS_REGISTER_NODE(nekomimi_bot::NekomimiBotWheelMain)