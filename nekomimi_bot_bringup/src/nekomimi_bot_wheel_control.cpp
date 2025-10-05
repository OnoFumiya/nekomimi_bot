#include "nekomimi_bot_bringup/nekomimi_bot_wheel_control.hpp"

std::array<double, 3> NekomimiBotWheelControl::setWheels(const geometry_msgs::msg::Twist vel_twist, std::array<double, 3> prev_wheels_vel) {
  std::array<double, 3> out = {
    0.0, // body_roll_joint [rad]
    0.0, // left_wheel      [rad/s]
    0.0  // right_wheel     [rad/s]
  };
  return out;
}
