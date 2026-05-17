cmake_minimum_required(VERSION 3.10.2)
project(nekomimi_bot_bringup)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclcpp_components REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(std_msgs REQUIRED)
find_package(ament_index_cpp REQUIRED)
find_package(tf2 REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(tf2_geometry_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(trajectory_msgs REQUIRED)
find_package(control_msgs REQUIRED)

###########
## Build ##
###########

## Include directories
include_directories(include)

# Library
add_library(${PROJECT_NAME} SHARED
  src/nekomimi_bot_wheel_control.cpp
  src/nekomimi_bot_wheel_odometry.cpp
  src/nekomimi_bot_wheel_main.cpp
)

rclcpp_components_register_node(${PROJECT_NAME}
  PLUGIN "nekomimi_bot::NekomimiBotWheelController"
  EXECUTABLE nekomimi_bot_wheel_node)

# ament_target_dependencies(${PROJECT_NAME}
#   rclcpp
#   rclcpp_components
#   geometry_msgs
#   std_msgs
#   ament_index_cpp
#   tf2
#   tf2_ros
#   tf2_geometry_msgs
#   nav_msgs
#   sensor_msgs
#   trajectory_msgs
#   control_msgs
# )
target_link_libraries(${PROJECT_NAME}
  rclcpp::rclcpp
  rclcpp_components::component
  ament_index_cpp::ament_index_cpp
  tf2::tf2
  tf2_ros::tf2_ros
  ${geometry_msgs_TARGETS}
  ${std_msgs_TARGETS}
  ${tf2_geometry_msgs_TARGETS}
  ${nav_msgs_TARGETS}
  ${sensor_msgs_TARGETS}
  ${trajectory_msgs_TARGETS}
  ${control_msgs_TARGETS}
)

install(TARGETS ${PROJECT_NAME}
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION bin)


install(DIRECTORY
  launch
  rviz
  config
  sound_files
  DESTINATION share/${PROJECT_NAME}
)
install(DIRECTORY
  include/${PROJECT_NAME}
  DESTINATION include
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # the following line skips the linter which checks for copyrights
  # comment the line when a copyright and license is added to all source files
  set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips cpplint (only works in a git repo)
  # comment the line when this package is in a git repo and when
  # a copyright and license is added to all source files
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
