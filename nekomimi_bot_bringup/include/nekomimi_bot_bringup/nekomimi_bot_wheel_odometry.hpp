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
  int CYCLE_FEQUENCY;
  double WHEEL_DISTANCE;   // Wheel Distance between left and right [m]
  double WHEEL_RADIUS;     // Wheel Radius [m]

  double current_body_roll_pos = 0.;
  double current_drive_pos[2] = {0, };
  double prev_body_roll_pos = 0.;
  double prev_drive_pos[2] = {0, };

  nav_msgs::msg::Odometry odom_;

  NekomimiBotWheelOdometry(rclcpp::Node* node) : node_(node) {
    // get parameter
    CYCLE_FEQUENCY = node_->get_parameter("cycle_fequency").as_int();
    WHEEL_DISTANCE = node_->get_parameter("wheel_distance").as_double();
    WHEEL_RADIUS = node_->get_parameter("wheel_radius").as_double();
    RCLCPP_INFO(node_->get_logger(), "NekoMimi Bot Wheel Odometry initialized.");

    // Broadcaster initialize
    tf_broadcaster_ = std::make_unique<tf2_ros::TransformBroadcaster>(node_);
  }
  ~NekomimiBotWheelOdometry() {
    RCLCPP_INFO(node_->get_logger(), "NekoMimi Bot Wheel Odometry destroyed.");
  }

  void update_odom();

  double distance_calculation(double wheel_delta_pos);
  void pose_broadcaster();
};

#endif // NEKOMIMI_BOT_WHEEL_ODOMETRY_HPP_