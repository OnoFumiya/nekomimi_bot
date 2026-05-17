cmake_minimum_required(VERSION 3.10)
project(nekomimi_bot_library)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclcpp_action REQUIRED)
find_package(rclcpp_components REQUIRED)
find_package(nekomimi_bot_interfaces REQUIRED)
find_package(std_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(trajectory_msgs REQUIRED)
find_package(tf2_geometry_msgs REQUIRED)

# Find libraries
include_directories(include)

# Library
add_library(${PROJECT_NAME} SHARED
  src/nekomimi_bot_joint_action_server.cpp
  src/nekomimi_bot_wheel_action_server.cpp
)

rclcpp_components_register_node(${PROJECT_NAME}
  PLUGIN "nekomimi_bot::JointActionServer"
  EXECUTABLE joint_action_server)
rclcpp_components_register_node(${PROJECT_NAME}
  PLUGIN "nekomimi_bot::WheelActionServer"
  EXECUTABLE wheel_action_server)


# ament_target_dependencies(${PROJECT_NAME}
#   "rclcpp"
#   "rclcpp_action"
#   "rclcpp_components"
#   "nekomimi_bot_interfaces"
#   "std_msgs"
#   "sensor_msgs"
#   "geometry_msgs"
#   "nav_msgs"
#   "trajectory_msgs"
#   "tf2_geometry_msgs")
target_link_libraries(${PROJECT_NAME}
  rclcpp::rclcpp
  rclcpp_action::rclcpp_action
  rclcpp_components::component
  ${nekomimi_bot_interfaces_TARGETS}
  ${std_msgs_TARGETS}
  ${sensor_msgs_TARGETS}
  ${geometry_msgs_TARGETS}
  ${nav_msgs_TARGETS}
  ${trajectory_msgs_TARGETS}
  ${tf2_geometry_msgs_TARGETS}
)


install(TARGETS ${PROJECT_NAME}
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION bin)

install(DIRECTORY
  config
  launch
  DESTINATION share/${PROJECT_NAME}
)

install(
  DIRECTORY include/${PROJECT_NAME}
  DESTINATION include
)


ament_package()
