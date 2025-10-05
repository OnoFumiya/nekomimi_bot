#include "nekomimi_bot_bringup/nekomimi_bot_wheel_main.hpp"

namespace nekomimi_bot {

NekomimiBotWheelMain::NekomimiBotWheelMain(const rclcpp::NodeOptions & options = rclcpp::NodeOptions())
: Node("nekomimi_bot_wheel_main", options)
{
  // Start up sound
  sound_play("start_up");

  // declare_parameter for each parameter
  this->declare_parameter("max_motor_velocity", (2.*M_PI));
  this->declare_parameter("wheel_diameter", 0.05);
  this->declare_parameter("wheel_distance", 0.15);
  this->declare_parameter("odometry_rate", 10);
  this->declare_parameter("body_roll_min", -M_PI/2.); // -INFINITY
  this->declare_parameter("body_roll_max",  M_PI/2.); //  INFINITY

  // Initialize the control and odometry classes
  nekomimi_bot_wheel_control_  = std::make_unique<NekomimiBotWheelControl>(this);
  nekomimi_bot_wheel_odometry_ = std::make_unique<NekomimiBotWheelOdometry>(this);

  // Configure the QoS profile
  rclcpp::QoS qos_profile(1);
  // qos_profile.reliability(RMW_QOS_POLICY_RELIABILITY_BEST_EFFORT);
  qos_profile.reliability(RMW_QOS_POLICY_RELIABILITY_RELIABLE);
  qos_profile.history(RMW_QOS_POLICY_HISTORY_KEEP_LAST);
  qos_profile.durability(RMW_QOS_POLICY_DURABILITY_VOLATILE);

  sub_vel_ = this->create_subscription<geometry_msgs::msg::Twist>(
      "cmd_vel", qos_profile, std::bind(&NekomimiBotWheelMain::vel_callback, this, std::placeholders::_1));
  sub_joint_info_ = this->create_subscription<sensor_msgs::msg::JointState>(
      "joint_states", qos_profile, std::bind(&NekomimiBotWheelMain::joint_callback, this, std::placeholders::_1));

  pub_odometry_ = this->create_publisher<nav_msgs::msg::Odometry>(
      "odom", qos_profile);
  pub_body_roll_joint_ = this->create_publisher<trajectory_msgs::msg::JointTrajectory>(
      "joint_trajectory_controller/joint_trajectory", qos_profile);
  pub_wheel_vel_ = this->create_publisher<std_msgs::msg::Float64MultiArray>(
      "velocity_controller/commands", qos_profile);

  // initialize
  is_twist_callback_ = false;

  // Set the initial position of the wheel
  joints_pos.clear();
  wheels_prev_pos.clear();
  wheels_curt_pos.clear();
  while (joints_pos.empty()) rclcpp::spin_some(this->get_node_base_interface());
  wheels_prev_pos["body_roll_joint"] = wheels_curt_pos["body_roll_joint"] = joints_pos["body_roll_joint"];
  wheels_prev_pos["left_wheel"]      = wheels_curt_pos["left_wheel"]      = joints_pos["left_wheel"];
  wheels_prev_pos["right_wheel"]     = wheels_curt_pos["right_wheel"]     = joints_pos["right_wheel"];
  prev_wheels_vel[0] = set_wheels_vel[0] = joints_pos["body_roll_joint"];
  prev_wheels_vel[1] = set_wheels_vel[1] = 0.;
  prev_wheels_vel[2] = set_wheels_vel[2] = 0.;

  // Get the robot namespace
  robot_name = (std::strcmp(this->get_namespace(), "/") != 0)
              ? std::string(this->get_namespace()).substr(1) + "/"
              : "";
  
  // Initilize Odometry
  result_odom.header.stamp    = this->get_clock()->now();
  result_odom.header.frame_id = robot_name + "odom";
  result_odom.child_frame_id  = robot_name + "base_footprint";

  prev_odom = result_odom;

  // create looped function of `odometry_rate`[hz]
  control_timer_ = this->create_wall_timer(
      std::chrono::milliseconds(static_cast<int>(1000. / this->get_parameter("odometry_rate").as_int())),
      std::bind(&NekomimiBotWheelMain::controller, this));

  RCLCPP_INFO(this->get_logger(), "NekomimiBotWheelMain initialized.");
}

NekomimiBotWheelMain::~NekomimiBotWheelMain()
{
  // Shut down sound
  sound_play("shut_down");
}

// Twist callback
void NekomimiBotWheelMain::vel_callback(const geometry_msgs::msg::Twist::SharedPtr vel_twist)
{
  vel_twist_ = *vel_twist;
  is_twist_callback_ = true;
}

void NekomimiBotWheelMain::joint_callback(const sensor_msgs::msg::JointState::SharedPtr joint_info)
{
  for (size_t i = 0; i < joint_info->name.size(); ++i) 
    joints_pos[joint_info->name[i]] = joint_info->position[i];
}

// start_up / shut_down sound
void NekomimiBotWheelMain::sound_play(std::string sound_name)
{
  // Get the package path
  std::string package_path = ament_index_cpp::get_package_share_directory("nekomimi_bot_bringup");
  std::string sound_path   = package_path + "/sound_files/" + sound_name + ".mp3";

  // Log output
  RCLCPP_INFO(this->get_logger(), "Sound File Name : [%s]", sound_name.c_str());

  // sound debug
  if (std::system(("mpg321 --quiet " + sound_path + " &").c_str())) 
    RCLCPP_ERROR(this->get_logger(), "There was an error reproducing the shutdown sound.");
}

// Control wheel
void NekomimiBotWheelMain::controller() {

  // Waiting for joint_states to be published...
  if (joints_pos.empty())  return;

  if (is_twist_callback_) {
    // calculate the wheels
    set_wheels_vel = nekomimi_bot_wheel_control_->setWheels(vel_twist_, prev_wheels_vel);
    prev_wheels_vel = set_wheels_vel;

    // Set body roll [rad]
    body_roll_joint_trajectory.joint_names.clear();
    body_roll_joint_trajectory.points.clear();
    setPosJointTrajectory("body_roll_joint", set_wheels_vel[0], 1./this->get_parameter("odometry_rate").as_int(), &body_roll_joint_trajectory);

    // Set Float64MultiArray [rad/s]
    wheel_joint_vel.data.clear();
    wheel_joint_vel.data.push_back(set_wheels_vel[1]);
    wheel_joint_vel.data.push_back(set_wheels_vel[2]);

    // Publish roll and wheels
    pub_body_roll_joint_->publish(body_roll_joint_trajectory);
    pub_wheel_vel_->publish(wheel_joint_vel);
  }

  // Update the current wheel position
  wheels_curt_pos["body_roll_joint"] = joints_pos["body_roll_joint"];
  wheels_curt_pos["left_wheel"]      = joints_pos["left_wheel"];
  wheels_curt_pos["right_wheel"]     = joints_pos["right_wheel"];

  // Calculate Odometry
  result_odom = nekomimi_bot_wheel_odometry_->odom(wheels_curt_pos, wheels_prev_pos, prev_odom);

  // Publish Odometry
  result_odom.header.stamp    = this->get_clock()->now();
  result_odom.header.frame_id = robot_name + "odom";
  result_odom.child_frame_id  = robot_name + "base_footprint";
  nekomimi_bot_wheel_odometry_->pose_broadcaster(result_odom);
  pub_odometry_->publish(result_odom);

  // Update wheel position value for next loop calculation
  wheels_prev_pos["body_roll_joint"] = wheels_curt_pos["body_roll_joint"];
  wheels_prev_pos["left_wheel"]      = wheels_curt_pos["left_wheel"];
  wheels_prev_pos["right_wheel"]     = wheels_curt_pos["right_wheel"];

  // Update odom for next loop calculation
  prev_odom = result_odom;
}

} // namespace sobit_pro