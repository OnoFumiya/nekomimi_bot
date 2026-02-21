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
  double BODY_ROLL_MAX_VEL;        // Body Roll moter's max speed [rad/s]
  double DRIVE_MAX_VEL;            // Driving moter's max speed [rad/s]
  double WHEEL_DISTANCE;           // Wheel Distance between left and right [m]
  double WHEEL_RADIUS;             // Wheel Radius [m]
  int CYCLE_FEQUENCY;              // Process Rate [Hz]
  bool BODY_ROLL_SMALL_RANGE;      // 
  double DRIVING_STATUS_THRESHOLD; // 

  double goal_body_roll_pos = 0.;
  double goal_drive_vel[2] = {0, };
  double current_body_roll_pos = 0.;

  geometry_msgs::msg::Twist vel_twist;

  // Constructor
  NekomimiBotWheelControl(rclcpp::Node* node) : node_(node) {
    // get parameter
    BODY_ROLL_MAX_VEL = node_->get_parameter("body_roll_max_vel").as_double();
    DRIVE_MAX_VEL = node_->get_parameter("drive_max_vel").as_double();
    WHEEL_DISTANCE = node_->get_parameter("wheel_distance").as_double();
    WHEEL_RADIUS = node_->get_parameter("wheel_radius").as_double();
    CYCLE_FEQUENCY = node_->get_parameter("cycle_fequency").as_int();
    BODY_ROLL_SMALL_RANGE = node_->get_parameter("body_roll_small_range").as_bool();
    DRIVING_STATUS_THRESHOLD = node_->get_parameter("driving_status_threshold").as_double();

    RCLCPP_INFO(node_->get_logger(), "NekoMimi Bot Wheel Control initialized.");
  }
  // Destructor
  ~NekomimiBotWheelControl() {
    RCLCPP_INFO(node_->get_logger(), "NekoMimi Bot Wheel Control destroyed.");
  }

  void twist_callback(const geometry_msgs::msg::Twist::SharedPtr vel_info);
  void update_wheel_goals();
};

#endif // NEKOMIMI_BOT_WHEEL_CONTROL_HPP_