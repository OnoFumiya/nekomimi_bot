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

  double body_roll_diff = current_body_roll_pos - prev_body_roll_pos;
  double base_rad = prev_yaw + body_roll_diff / 2.;

  if ((0 < (distance_m[0] * distance_m[1])) && (fabsf(distance_m[0] - distance_m[1]) < 0.001)) {   // Translational motion
    result_odom.pose.pose.position.x = odom_.pose.pose.position.x + 
        distance_m[0] * cos((current_body_roll_pos + prev_body_roll_pos) / 2. + base_rad);
    result_odom.pose.pose.position.y = odom_.pose.pose.position.y + 
        distance_m[0] * sin((current_body_roll_pos + prev_body_roll_pos) / 2. + base_rad);
  } else {
    double diff_yaw = (distance_m[1] - distance_m[0]) / WHEEL_DISTANCE;
    result_odom.pose.pose.position.x = odom_.pose.pose.position.x + 
        (distance_m[0] + distance_m[1]) / 2. * cos((current_body_roll_pos + prev_body_roll_pos) / 2. + base_rad + diff_yaw / 2.);
    result_odom.pose.pose.position.y = odom_.pose.pose.position.y + 
        (distance_m[0] + distance_m[1]) / 2. * sin((current_body_roll_pos + prev_body_roll_pos) / 2. + base_rad + diff_yaw / 2.);
    base_rad += diff_yaw;
  }

  // Change quaternion
  quat_tf.setRPY(0., 0., base_rad - 3. * body_roll_diff / 2.);
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