#include "nekomimi_bot_bringup/nekomimi_bot_wheel_control.hpp"

void NekomimiBotWheelControl::twist_callback(const geometry_msgs::msg::Twist::SharedPtr vel_info) {
  vel_twist = *vel_info;
}

void NekomimiBotWheelControl::update_wheel_goals() {

  if ((vel_twist.linear.x == 0.) && (vel_twist.linear.y == 0.) && (vel_twist.angular.z == 0.)) {
    goal_body_roll_vel = 0.;
    goal_drive_vel[0] = goal_drive_vel[1] = 0.;
  } else if ((vel_twist.linear.x == 0.) && (vel_twist.linear.y == 0.)) {
    goal_body_roll_vel = 0.;
    goal_drive_vel[0] = -(WHEEL_DISTANCE/2.) * vel_twist.angular.z / WHEEL_RADIUS;
    goal_drive_vel[1] =  (WHEEL_DISTANCE/2.) * vel_twist.angular.z / WHEEL_RADIUS;
  } else {

    double goal_base_rad = std::atan2(vel_twist.linear.y, vel_twist.linear.x);
    int pn = 1;

    while (fabsf(goal_base_rad - current_body_roll_pos) > M_PI/2.) {
      goal_base_rad -= M_PI * (goal_base_rad - current_body_roll_pos) / fabsf(goal_base_rad - current_body_roll_pos);
      pn *= -1;
    }

    if (fabsf(goal_base_rad) > ((BODY_ROLL_RANGE < M_PI) ? M_PI/2. : BODY_ROLL_RANGE/2.)) {
    // if (fabsf(goal_base_rad) >= BODY_ROLL_RANGE/2.+0.01) {
      goal_base_rad -= M_PI * goal_base_rad / fabsf(goal_base_rad);
      pn *= -1;
    }

    if (fabsf(goal_base_rad - current_body_roll_pos) < (BODY_ROLL_MAX_VEL/CYCLE_FEQUENCY)) {
      if (fabs(goal_base_rad - current_body_roll_pos) < DRIVING_STATUS_THRESHOLD) {
        goal_body_roll_vel = 0.;
        if (vel_twist.angular.z == 0.) {
          goal_drive_vel[0] =  pn * std::sqrt(std::pow(vel_twist.linear.x, 2.) + std::pow(vel_twist.linear.y, 2.)) / WHEEL_RADIUS;
          goal_drive_vel[1] =  pn * std::sqrt(std::pow(vel_twist.linear.x, 2.) + std::pow(vel_twist.linear.y, 2.)) / WHEEL_RADIUS;
        } else {
          double r = std::sqrt(std::pow(vel_twist.linear.x, 2.) + std::pow(vel_twist.linear.y, 2.)) / std::fabs(vel_twist.angular.z);
          int angular_pn = vel_twist.angular.z / std::fabs(vel_twist.angular.z);
          goal_drive_vel[0] =  pn * (r - angular_pn * pn * WHEEL_DISTANCE/2.) * std::fabs(vel_twist.angular.z) / WHEEL_RADIUS;
          goal_drive_vel[1] =  pn * (r + angular_pn * pn * WHEEL_DISTANCE/2.) * std::fabs(vel_twist.angular.z) / WHEEL_RADIUS;
        }
      } else {
        goal_body_roll_vel = (goal_base_rad - current_body_roll_pos) * CYCLE_FEQUENCY / 3.;
        goal_drive_vel[0] = -goal_body_roll_vel * (WHEEL_DISTANCE/2.) / WHEEL_RADIUS;
        goal_drive_vel[1] =  goal_body_roll_vel * (WHEEL_DISTANCE/2.) / WHEEL_RADIUS;
      }
    } else {
      goal_body_roll_vel = BODY_ROLL_MAX_VEL * (goal_base_rad - current_body_roll_pos) / fabsf(goal_base_rad - current_body_roll_pos) / 3.;
      goal_drive_vel[0] = -goal_body_roll_vel * (WHEEL_DISTANCE/2.) / WHEEL_RADIUS;
      goal_drive_vel[1] =  goal_body_roll_vel * (WHEEL_DISTANCE/2.) / WHEEL_RADIUS;
    }
  }

}
