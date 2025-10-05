#include "nekomimi_bot_bringup/nekomimi_bot_wheel_odometry.hpp"

// Calculate Odometry
nav_msgs::msg::Odometry NekomimiBotWheelOdometry::odom(
  std::map<std::string, double> wheels_curt_pos,
  std::map<std::string, double> wheels_prev_pos,
  nav_msgs::msg::Odometry prev_odom)
{
  nav_msgs::msg::Odometry result_odom;

  // get the movement of each wheel[m]
  std::map<std::string, double> distance_m;
  distance_m["left_wheel"]  = distance_calculation(wheels_curt_pos["left_wheel"]  - wheels_prev_pos["left_wheel"]);
  distance_m["right_wheel"] = distance_calculation(wheels_curt_pos["right_wheel"] - wheels_prev_pos["right_wheel"]);

  // Transform to Roll, Pitch and Yaw from prev_odom
  tf2::Quaternion quat_tf;
  double prev_roll, prev_pitch, prev_yaw;
  tf2::fromMsg(prev_odom.pose.pose.orientation, quat_tf);
  tf2::Matrix3x3(quat_tf).getRPY(prev_roll, prev_pitch, prev_yaw);

  double diff_x = 0.,diff_y = 0., diff_yaw = 0.;
  /*
  diff_x
  diff_y
  diff_yaw
  */

  // Update the Odometry
  result_odom.pose.pose.position.x = prev_odom.pose.pose.position.x + 
      diff_x * cos(prev_yaw) - diff_y * sin(prev_yaw);
  result_odom.pose.pose.position.y = prev_odom.pose.pose.position.y + 
      diff_x * sin(prev_yaw) + diff_y * cos(prev_yaw);
  result_odom.pose.pose.position.z = prev_odom.pose.pose.position.z;

  // Change quaternion
  quat_tf.setRPY(0., 0., (prev_yaw + diff_yaw));
  tf2::convert(quat_tf, result_odom.pose.pose.orientation);

  return result_odom;
}

// Distance calculation
double NekomimiBotWheelOdometry::distance_calculation(double wheel_delta_pos) {
  return WHEEL_DIAMETER/2. * wheel_delta_pos;
}

// Pose broadcaster (Generate a pose from Odometry)
void NekomimiBotWheelOdometry::pose_broadcaster(const nav_msgs::msg::Odometry &tf_odom) {
  geometry_msgs::msg::TransformStamped transformStamped;

  transformStamped.header          = tf_odom.header;
  transformStamped.child_frame_id  = tf_odom.child_frame_id;

  transformStamped.transform.translation.x = tf_odom.pose.pose.position.x;
  transformStamped.transform.translation.y = tf_odom.pose.pose.position.y;
  transformStamped.transform.translation.z = tf_odom.pose.pose.position.z;
  transformStamped.transform.rotation      = tf_odom.pose.pose.orientation;

  tf_broadcaster_->sendTransform(transformStamped);
}