#ifndef NEKOMIMI_BOT_WHEEL_CONTROL_HPP_
#define NEKOMIMI_BOT_WHEEL_CONTROL_HPP_

#include <cmath>
#include <array>
#include <chrono>

#include <geometry_msgs/msg/twist.hpp>
#include <geometry_msgs/msg/point.hpp>

#include <rclcpp/rclcpp.hpp>

class NekomimiBotWheelControl {
private:
  rclcpp::Node* node_;

public:

  // robot parameters
  double LIMIT_VEL_VALUE;
  double WHEEL_DIAMETER;
  double WHEEL_DISTANCE;
  int ODOMETRY_RATE;
  std::array<double, 2> BODY_ROTATE_LIMIT;

  // Constructor
  NekomimiBotWheelControl(rclcpp::Node* node) : node_(node) {

    // get parameter
    LIMIT_VEL_VALUE = node_->get_parameter("max_motor_velocity").as_double();
    WHEEL_DIAMETER = node_->get_parameter("wheel_diameter").as_double();
    WHEEL_DISTANCE = node_->get_parameter("wheel_distance").as_double();
    ODOMETRY_RATE = node_->get_parameter("odometry_rate").as_int();
    BODY_ROTATE_LIMIT[0] = node_->get_parameter("body_roll_min").as_double();
    BODY_ROTATE_LIMIT[1] = node_->get_parameter("body_roll_max").as_double();

    RCLCPP_INFO(node_->get_logger(), "NekomimiBotWheelControl initialized.");
  }
  // Destructor
  ~NekomimiBotWheelControl() {
    RCLCPP_INFO(node_->get_logger(), "NekomimiBotWheelControl destroyed.");
  }

  std::array<double, 3> setWheels(const geometry_msgs::msg::Twist vel_twist, const std::array<double, 3> prev_wheels_vel);
};

#endif // NEKOMIMI_BOT_WHEEL_CONTROL_HPP_