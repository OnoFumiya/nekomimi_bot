#include "nekomimi_bot_bringup/nekomimi_bot_wheel_main.hpp"

namespace nekomimi_bot {

NekomimiBotWheelController::NekomimiBotWheelController(const rclcpp::NodeOptions & options = rclcpp::NodeOptions())
: Node("nekomimi_bot_wheel_controller", options) {
  // declare_parameter for each parameter
  this->declare_parameter("robot_base_frame", "base_footprint");
  this->declare_parameter("twist_topic", "cmd_vel");
  this->declare_parameter("rotate_controller_name", "rotate_controller");
  this->declare_parameter("wheel_controller_name", "wheel_controller");
  this->declare_parameter("body_roll_max_vel", (2.*M_PI));
  this->declare_parameter("drive_max_vel", M_PI);
  this->declare_parameter("wheel_radius", 0.05);
  this->declare_parameter("wheel_distance", 0.15);
  this->declare_parameter("cycle_fequency", 10);
  this->declare_parameter("body_roll_joint", "body_roll_joint");
  this->declare_parameter("drive_joints", std::vector<std::string>({"wheel_drive_l_joint", "wheel_drive_r_joint"}));
  this->declare_parameter("body_roll_range", -1.);
  this->declare_parameter("driving_status_threshold", 0.26);


  body_roll_joint_name = this->get_parameter("body_roll_joint").as_string();
  drive_joints_names   = this->get_parameter("drive_joints").as_string_array();

  if (drive_joints_names.size() != 2) return;

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
      this->get_parameter("twist_topic").as_string(), qos_profile, std::bind(&NekomimiBotWheelControl::twist_callback, nekomimi_bot_wheel_control_.get(), std::placeholders::_1));
  sub_joint_info_ = this->create_subscription<sensor_msgs::msg::JointState>(
      "joint_states", qos_profile, std::bind(&NekomimiBotWheelController::joint_callback, this, std::placeholders::_1));

  pub_odometry_ = this->create_publisher<nav_msgs::msg::Odometry>(
      "odom", qos_profile);
  pub_body_roll_vel_ = this->create_publisher<std_msgs::msg::Float64MultiArray>(
      this->get_parameter("rotate_controller_name").as_string() + "/commands", qos_profile);
  pub_wheel_vel_ = this->create_publisher<std_msgs::msg::Float64MultiArray>(
      this->get_parameter("wheel_controller_name").as_string() + "/commands", qos_profile);

  // Set the initial position of the wheel
  joints_pos.clear();
  while (joints_pos.empty()) rclcpp::spin_some(this->get_node_base_interface());

  nekomimi_bot_wheel_control_->goal_body_roll_vel = 0.;
  nekomimi_bot_wheel_odometry_->prev_body_roll_pos = nekomimi_bot_wheel_control_->current_body_roll_pos = nekomimi_bot_wheel_odometry_->current_body_roll_pos = joints_pos[body_roll_joint_name];
  for (int i=0; i<2; i++) {
    nekomimi_bot_wheel_control_->goal_drive_vel[i] = 0.;
    nekomimi_bot_wheel_odometry_->prev_drive_pos[i] = nekomimi_bot_wheel_odometry_->current_drive_pos[i] = joints_pos[drive_joints_names[i]];
  }

  // create looped function of 50hz
  control_timer_ = this->create_wall_timer(
      std::chrono::milliseconds((int)(1000. / this->get_parameter("cycle_fequency").as_int())),
      std::bind(&NekomimiBotWheelController::control_callback, this));

  // Get the robot namespace
  std::string robot_name = (std::strcmp(this->get_namespace(), "/") != 0)
                          ? std::string(this->get_namespace()).substr(1) + "/"
                          : "";
  
  // Initilize Odometry
  nekomimi_bot_wheel_odometry_->odom_.header.stamp    = this->get_clock()->now();
  nekomimi_bot_wheel_odometry_->odom_.header.frame_id = robot_name + "odom";
  nekomimi_bot_wheel_odometry_->odom_.child_frame_id  = robot_name + this->get_parameter("robot_base_frame").as_string();;

  // Start up sound
  sound_play("start_up");

  RCLCPP_INFO(this->get_logger(), "NekoMimi Bot Wheel Main initialized.");
}

NekomimiBotWheelController::~NekomimiBotWheelController() {
  RCLCPP_INFO(this->get_logger(), "NekoMimi Bot Wheel Main destroyed.");
  // Shut down sound
  sound_play("shut_down");
}

void NekomimiBotWheelController::joint_callback(const sensor_msgs::msg::JointState::SharedPtr joint_info) {
  for (size_t i = 0; i < joint_info->name.size(); ++i) 
    joints_pos[joint_info->name[i]] = joint_info->position[i];
}

// start_up / shut_down sound
void NekomimiBotWheelController::sound_play(std::string sound_name) {
  // Get the package path
  std::string package_path = ament_index_cpp::get_package_share_directory("nekomimi_bot_bringup");
  std::string sound_path   = package_path + "/sound_files/" + sound_name + ".mp3";

  // Log output
  RCLCPP_INFO(this->get_logger(), "Sound File Name : [%s]", sound_name.c_str());

  // sound play
  std::system(("mpg321 --quiet " + sound_path + " &").c_str());
}

// Control wheel
void NekomimiBotWheelController::control_callback() {

  // Waiting for joint_states to be published...
  if (joints_pos.empty())  return;

  nekomimi_bot_wheel_control_->update_wheel_goals();

  // Update current steer positions
  nekomimi_bot_wheel_control_->current_body_roll_pos = nekomimi_bot_wheel_odometry_->current_body_roll_pos = joints_pos[body_roll_joint_name];
  for (int i=0; i<2; i++) nekomimi_bot_wheel_odometry_->current_drive_pos[i] = joints_pos[drive_joints_names[i]];

  // Set Body Roll [rad/s]
  body_roll_joint_vel.data.clear();
  body_roll_joint_vel.data.push_back(nekomimi_bot_wheel_control_->goal_body_roll_vel);

  // Set Wheels Vellocity
  wheel_joint_vel.data.clear();
  for (int i=0; i<2; i++)
    wheel_joint_vel.data.push_back(nekomimi_bot_wheel_control_->goal_drive_vel[i]);

  // Publish Float64MultiArray of Body Roll [rad/s]
  pub_body_roll_vel_->publish(body_roll_joint_vel);

  // Publish Float64MultiArray of Wheels [rad/s]
  pub_wheel_vel_->publish(wheel_joint_vel);

  // Calculate Odometry
  nekomimi_bot_wheel_odometry_->update_odom();

  // Publish Odometry
  nekomimi_bot_wheel_odometry_->pose_broadcaster();
  pub_odometry_->publish(nekomimi_bot_wheel_odometry_->odom_);

  // Update Previous data
  nekomimi_bot_wheel_odometry_->prev_body_roll_pos = nekomimi_bot_wheel_odometry_->current_body_roll_pos;
  for (int i=0; i<2; i++)
    nekomimi_bot_wheel_odometry_->prev_drive_pos[i] = nekomimi_bot_wheel_odometry_->current_drive_pos[i];
}

} // namespace nekomimi_bot