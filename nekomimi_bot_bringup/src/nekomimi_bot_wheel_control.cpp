#include "nekomimi_bot_bringup/nekomimi_bot_wheel_control.hpp"

std::array<double, 3> NekomimiBotWheelControl::setWheels(const geometry_msgs::msg::Twist vel_twist, std::array<double, 3> prev_wheels_vel) {
  std::array<double, 3> out = {
    0.0, // body_roll_joint [rad]
    0.0, // left_wheel      [rad/s]
    0.0  // right_wheel     [rad/s]
  };

  if (std::fabs(prev_wheels_vel[0] - std::atan2(vel_twist.linear.y, vel_twist.linear.x)) < (LIMIT_VEL_VALUE/ODOMETRY_RATE)) {
    out[0] = std::atan2(vel_twist.linear.y, vel_twist.linear.x);
    if (vel_twist.angular.z == 0.) {
      out[1] =  std::sqrt(std::pow(vel_twist.linear.x, 2.) + std::pow(vel_twist.linear.y, 2.));
      out[2] = -std::sqrt(std::pow(vel_twist.linear.x, 2.) + std::pow(vel_twist.linear.y, 2.));
    }
  } else if (std::fabs(M_PI - std::fabs(prev_wheels_vel[0] - std::atan2(vel_twist.linear.y, vel_twist.linear.x))) < (LIMIT_VEL_VALUE/ODOMETRY_RATE)) {}

  return out;
}
