#include "nekomimi_bot_bringup/nekomimi_bot_wheel_odometry.hpp"

// Calculate Odometry
void NekomimiBotWheelOdometry::update_odom()
{
  nav_msgs::msg::Odometry result_odom = odom_;

  // get the movement of each wheel[m]
  std::vector<double> distance_m(2);
  for (int i=0; i<2; i++)
    distance_m[i] = distance_calculation(current_drive_pos[i] - prev_drive_pos[i]);

  // Transform to Roll, Pitch and Yaw from  previous odom
  tf2::Quaternion quat_tf;
  double prev_roll, prev_pitch, prev_yaw;
  tf2::fromMsg(odom_.pose.pose.orientation, quat_tf);
  tf2::Matrix3x3(quat_tf).getRPY(prev_roll, prev_pitch, prev_yaw);

  double diff_x = 0.,diff_y = 0., diff_yaw = 0.;
  /*
  diff_x
  diff_y
  diff_yaw
  */
  diff_yaw -= current_body_roll_pos - prev_body_roll_pos;

  double base_rad = (current_body_roll_pos + prev_body_roll_pos) / 2.;
  if ((0 < (distance_m[0] * distance_m[1])) && (fabsf(distance_m[0] - distance_m[1]) < 0.001)) {   // Translational motion
    diff_x = (distance_m[0] + distance_m[1]) / 2.;
  } else {
    diff_yaw += (distance_m[1] - distance_m[0]) / WHEEL_DISTANCE;
    diff_x = (distance_m[0] + distance_m[1]) / 2.;
    // geometry_msgs::msg::Point base_center;
    // l / r = theta
    // dm[0] / r0 = theta = dm[1] / r1
  }
  // diff_x = ;

  // Update the Odometry
  result_odom.pose.pose.position.x = odom_.pose.pose.position.x + 
      diff_x * cos(prev_yaw + diff_yaw) - diff_y * sin(prev_yaw + diff_yaw);
  result_odom.pose.pose.position.y = odom_.pose.pose.position.y + 
      diff_x * sin(prev_yaw + diff_yaw) + diff_y * cos(prev_yaw + diff_yaw);

  // Change quaternion
  quat_tf.setRPY(0., 0., (prev_yaw + diff_yaw));
  tf2::convert(quat_tf, result_odom.pose.pose.orientation);

  result_odom.header.stamp = node_->get_clock()->now();
  odom_ = result_odom;
}

// Distance calculation
double NekomimiBotWheelOdometry::distance_calculation(double wheel_delta_pos) {
  if (M_PI < fabsf(wheel_delta_pos)) wheel_delta_pos -= 2*M_PI * wheel_delta_pos / fabsf(wheel_delta_pos);
  return WHEEL_RADIUS * wheel_delta_pos;
}

// Pose broadcaster (Generate a TF pose from Odometry)
void NekomimiBotWheelOdometry::pose_broadcaster() {
  geometry_msgs::msg::TransformStamped transformStamped;

  transformStamped.header          = odom_.header;
  transformStamped.child_frame_id  = odom_.child_frame_id;

  transformStamped.transform.translation.x = odom_.pose.pose.position.x;
  transformStamped.transform.translation.y = odom_.pose.pose.position.y;
  transformStamped.transform.translation.z = odom_.pose.pose.position.z;

  transformStamped.transform.rotation      = odom_.pose.pose.orientation;

  tf_broadcaster_->sendTransform(transformStamped);
}