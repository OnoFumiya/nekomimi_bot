#include "nekomimi_bot_bringup/nekomimi_bot_wheel_control.hpp"

void NekomimiBotWheelControl::twist_callback(const geometry_msgs::msg::Twist::SharedPtr vel_info) {
  vel_twist = *vel_info;
}

void NekomimiBotWheelControl::update_wheel_goals() {

  if ((vel_twist.linear.x == 0.) && (vel_twist.linear.y == 0.) && (vel_twist.angular.z == 0.)) {

    goal_body_roll_pos = current_body_roll_pos;
    goal_drive_vel[0] = goal_drive_vel[1] = 0.;
    // if ((float)(BODY_ROLL_MAX_VEL/((float)CYCLE_FEQUENCY)) < fabsf(current_body_roll_pos)) 
    //   goal_body_roll_pos = current_body_roll_pos - (float)(BODY_ROLL_MAX_VEL/((float)CYCLE_FEQUENCY)) * current_body_roll_pos / fabsf(current_body_roll_pos);
    // else 
    //   goal_body_roll_pos = 0.;

    // if (fabsf(current_body_roll_pos) < DRIVING_STATUS_THRESHOLD) 
    //   goal_drive_vel[0] = goal_drive_vel[1] = 0.;
    // else {
    //   goal_drive_vel[0] = -(goal_body_roll_pos - current_body_roll_pos) * CYCLE_FEQUENCY * (WHEEL_DISTANCE/2.) / WHEEL_RADIUS;
    //   goal_drive_vel[1] =  (goal_body_roll_pos - current_body_roll_pos) * CYCLE_FEQUENCY * (WHEEL_DISTANCE/2.) / WHEEL_RADIUS;
    // }

  } else if ((vel_twist.linear.x == 0.) && (vel_twist.linear.y == 0.)) {
    if ((current_body_roll_pos * vel_twist.angular.z) > 0.) {

      if ((float)(BODY_ROLL_MAX_VEL/((float)CYCLE_FEQUENCY)) < fabsf(current_body_roll_pos)) {
        goal_body_roll_pos = current_body_roll_pos - vel_twist.angular.z / ((float)CYCLE_FEQUENCY);
        goal_drive_vel[0] = 0.;
        goal_drive_vel[1] = 0.;
      } else {
        goal_body_roll_pos = 0.;
        goal_drive_vel[0] = -(WHEEL_DISTANCE/2.) * vel_twist.angular.z / WHEEL_RADIUS + (goal_body_roll_pos - current_body_roll_pos) * (WHEEL_DISTANCE/2.) / WHEEL_RADIUS;
        goal_drive_vel[1] =  (WHEEL_DISTANCE/2.) * vel_twist.angular.z / WHEEL_RADIUS - (goal_body_roll_pos - current_body_roll_pos) * (WHEEL_DISTANCE/2.) / WHEEL_RADIUS;
      }

    } else {
      goal_body_roll_pos = current_body_roll_pos;
      goal_drive_vel[0] = -(WHEEL_DISTANCE/2.) * vel_twist.angular.z / WHEEL_RADIUS;
      goal_drive_vel[1] =  (WHEEL_DISTANCE/2.) * vel_twist.angular.z / WHEEL_RADIUS;
    }
  } else {

    int pn;
    double goal_base_rad;
    if (BODY_ROLL_SMALL_RANGE) {
      if (fabsf(std::atan2(vel_twist.linear.y, vel_twist.linear.x)) < M_PI/2.) {
        goal_base_rad = std::atan2(vel_twist.linear.y, vel_twist.linear.x);
        pn = 1;
      } else {
        goal_base_rad = std::atan2(vel_twist.linear.y, vel_twist.linear.x) - M_PI * std::atan2(vel_twist.linear.y, vel_twist.linear.x) / fabsf(std::atan2(vel_twist.linear.y, vel_twist.linear.x));
        pn = -1;
      }

    } else {
      goal_base_rad = std::atan2(vel_twist.linear.y, vel_twist.linear.x);
      pn = 1;
      if ((std::fabs(goal_base_rad - M_PI*goal_base_rad/fabsf(goal_base_rad) - current_body_roll_pos) < std::fabs(goal_base_rad - current_body_roll_pos)) && 
          (std::fabs(goal_base_rad - M_PI*goal_base_rad/fabsf(goal_base_rad)) < M_PI)) {
        goal_base_rad -= M_PI*goal_base_rad/fabsf(goal_base_rad);
        pn = -1;
      }

    }

    if (std::fabs(goal_base_rad - current_body_roll_pos) < (float)(BODY_ROLL_MAX_VEL/((float)CYCLE_FEQUENCY))) 
      goal_body_roll_pos = goal_base_rad;
    else 
      goal_body_roll_pos = current_body_roll_pos + (float)(BODY_ROLL_MAX_VEL/((float)CYCLE_FEQUENCY)) * (goal_base_rad - current_body_roll_pos) / fabsf(goal_base_rad - current_body_roll_pos);


    if (vel_twist.angular.z == 0.) {
      goal_drive_vel[0] =  pn * std::sqrt(std::pow(vel_twist.linear.x, 2.) + std::pow(vel_twist.linear.y, 2.)) / WHEEL_RADIUS;
      goal_drive_vel[1] =  pn * std::sqrt(std::pow(vel_twist.linear.x, 2.) + std::pow(vel_twist.linear.y, 2.)) / WHEEL_RADIUS;
    } else {
      double r = std::sqrt(std::pow(vel_twist.linear.x, 2.) + std::pow(vel_twist.linear.y, 2.)) / std::fabs(vel_twist.angular.z);
      int angular_pn = vel_twist.angular.z / std::fabs(vel_twist.angular.z);
      goal_drive_vel[0] =  pn * (r - angular_pn * pn * WHEEL_DISTANCE/2.) * std::fabs(vel_twist.angular.z) / WHEEL_RADIUS;
      goal_drive_vel[1] =  pn * (r + angular_pn * pn * WHEEL_DISTANCE/2.) * std::fabs(vel_twist.angular.z) / WHEEL_RADIUS;
    }

    if (std::fabs(goal_base_rad - current_body_roll_pos) > DRIVING_STATUS_THRESHOLD) {
      goal_drive_vel[0] += (goal_body_roll_pos - current_body_roll_pos) * CYCLE_FEQUENCY * (WHEEL_DISTANCE/2.) / WHEEL_RADIUS;
      goal_drive_vel[1] -= (goal_body_roll_pos - current_body_roll_pos) * CYCLE_FEQUENCY * (WHEEL_DISTANCE/2.) / WHEEL_RADIUS;
    }
  }
}
