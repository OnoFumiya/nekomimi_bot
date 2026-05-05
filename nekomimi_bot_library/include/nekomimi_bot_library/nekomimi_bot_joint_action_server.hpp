#include <map>

#include "nekomimi_bot_interfaces/action/move_joint.hpp"
#include "nekomimi_bot_interfaces/action/move_to_pose.hpp"

#include "trajectory_msgs/msg/joint_trajectory.hpp"
#include "sensor_msgs/msg/joint_state.hpp"
#include "geometry_msgs/msg/transform_stamped.hpp"
#include "geometry_msgs/msg/quaternion.h"
#include "geometry_msgs/msg/vector3.h"
#include "geometry_msgs/msg/point.h"

#include <rclcpp/rclcpp.hpp>
#include <rclcpp_action/rclcpp_action.hpp>
#include <rclcpp_components/register_node_macro.hpp>


namespace nekomimi_bot
{

struct PoseParams 
{
  std::string pose_name;
  double head_pan_joint;
  double head_tilt_joint;
};


class JointActionServer : public rclcpp::Node
{
public:
  using MoveJoint = nekomimi_bot_interfaces::action::MoveJoint;
  using MoveToPose = nekomimi_bot_interfaces::action::MoveToPose;

  using GoalHandleMoveJoints = rclcpp_action::ServerGoalHandle<nekomimi_bot_interfaces::action::MoveJoint>;
  using GoalHandleMoveToPose = rclcpp_action::ServerGoalHandle<nekomimi_bot_interfaces::action::MoveToPose>;


  explicit JointActionServer(const rclcpp::NodeOptions & options);
  ~JointActionServer();

  trajectory_msgs::msg::JointTrajectory set_joints(
    const std::vector<std::string> &target_joint_names,
    const std::vector<double> &target_joint_rad,
    const builtin_interfaces::msg::Duration &time_allowance,
    const std::string &group_name);

private:
  const std::vector<std::string> JointNames = {
    "head_pan_joint",
    "head_tilt_joint",
  };

  const std::vector<std::string> JointNamesHead = {
    "head_pan_joint",
    "head_tilt_joint",
  };

  // static constexpr double DUMMY = 0.;

  std::vector<PoseParams> poses_;
  std::map<std::string, double> curt_joint_state_;

  rclcpp_action::Server<MoveJoint>::SharedPtr action_server_move_joints_;
  rclcpp_action::Server<MoveToPose>::SharedPtr action_server_move_to_pose_;

  rclcpp_action::GoalResponse handle_move_joints_goal(const rclcpp_action::GoalUUID & uuid, std::shared_ptr<const MoveJoint::Goal> goal);
  rclcpp_action::GoalResponse handle_move_to_pose_goal(const rclcpp_action::GoalUUID & uuid, std::shared_ptr<const MoveToPose::Goal> goal);

  rclcpp_action::CancelResponse handle_move_joints_cancel(const std::shared_ptr<GoalHandleMoveJoints> goal_handle);
  rclcpp_action::CancelResponse handle_move_to_pose_cancel(const std::shared_ptr<GoalHandleMoveToPose> goal_handle);

  void handle_move_joints_accepted(const std::shared_ptr<GoalHandleMoveJoints> goal_handle);
  void handle_move_to_pose_accepted(const std::shared_ptr<GoalHandleMoveToPose> goal_handle);

  void exe_move_joints(const std::shared_ptr<GoalHandleMoveJoints> goal_handle);
  void exe_move_to_pose(const std::shared_ptr<GoalHandleMoveToPose> goal_handle);

  rclcpp::Publisher<trajectory_msgs::msg::JointTrajectory>::SharedPtr pub_head_joint_control_;
  rclcpp::Subscription<sensor_msgs::msg::JointState>::SharedPtr sub_joint_state_;

  std::map<std::string, double> initial_joint_state_;


  void joint_state_callback(const sensor_msgs::msg::JointState::SharedPtr msg);
}; // class JointActionServer


} // namespace nekomimi_bot

RCLCPP_COMPONENTS_REGISTER_NODE(nekomimi_bot::JointActionServer)

