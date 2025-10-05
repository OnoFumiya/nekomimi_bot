#ifndef NEKOMIMI_BOT_WHEEL_ODOMETRY_HPP_
#define NEKOMIMI_BOT_WHEEL_ODOMETRY_HPP_

#include <cmath>
#include <memory>

#include <tf2_ros/transform_broadcaster.h>
#include <tf2/LinearMath/Quaternion.h>
#include <tf2/LinearMath/Matrix3x3.h>

#include <tf2_geometry_msgs/tf2_geometry_msgs.hpp>
#include <nav_msgs/msg/odometry.hpp>
#include <geometry_msgs/msg/point.hpp>

#include <rclcpp/rclcpp.hpp>

class NekomimiBotWheelOdometry {
private:
  rclcpp::Node* node_;
  std::unique_ptr<tf2_ros::TransformBroadcaster> tf_broadcaster_;

public:

  // robot parameters
  double LIMIT_VEL_VALUE;
  double WHEEL_DIAMETER;
  double WHEEL_DISTANCE;
  int ODOMETRY_RATE;
  std::array<double, 2> BODY_ROTATE_LIMIT;

  NekomimiBotWheelOdometry(rclcpp::Node* node) : node_(node) {
    RCLCPP_INFO(node_->get_logger(), "NekomimiBotWheelOdometry initialized.");

    // get parameter
    LIMIT_VEL_VALUE = node_->get_parameter("max_motor_velocity").as_double();
    WHEEL_DIAMETER = node_->get_parameter("wheel_diameter").as_double();
    WHEEL_DISTANCE = node_->get_parameter("wheel_distance").as_double();
    ODOMETRY_RATE = node_->get_parameter("odometry_rate").as_int();
    BODY_ROTATE_LIMIT[0] = node_->get_parameter("body_roll_min").as_double();
    BODY_ROTATE_LIMIT[1] = node_->get_parameter("body_roll_max").as_double();

    // Broadcaster initialize
    tf_broadcaster_ = std::make_unique<tf2_ros::TransformBroadcaster>(node_);
  }
  ~NekomimiBotWheelOdometry() {
  RCLCPP_INFO(node_->get_logger(), "NekomimiBotWheelOdometry destroyed.");
  }

  nav_msgs::msg::Odometry odom(
    std::map<std::string, double> wheels_curt_pos,
    std::map<std::string, double> wheels_prev_pos,
    nav_msgs::msg::Odometry prev_odom);

  double distance_calculation(double wheel_delta_pos);
  void pose_broadcaster(const nav_msgs::msg::Odometry &tf_odom);
};

#endif // NEKOMIMI_BOT_WHEEL_ODOMETRY_HPP_