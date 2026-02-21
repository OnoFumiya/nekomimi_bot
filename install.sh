#!/bin/bash

echo "╔══╣ Setup: NekoMimi Bot (STARTING) ╠══╗"


# Keep track of the current directory
DIR=`pwd`
cd ..

# Download required packages for NekoMimi Bot
ros_packages=(
    "feetech_ros2_driver"
    "hls_lfcd_lds_driver"
    "realsense_ros"
    # "gazebo_world"
)

#Clone all packages
for ((i = 0; i < ${#ros_packages[@]}; i++)) {
    echo "Clonning: ${ros_packages[i]}"
    git clone -b $ROS_DISTRO-devel https://github.com/OnoFumiya/${ros_packages[i]}.git

    # Check if install.sh exists in each package
    if [ -f ${ros_packages[i]}/install.sh ]; then
        echo "Running install.sh in ${ros_packages[i]}."
        cd ${ros_packages[i]}
        bash install.sh
        cd ..
    fi
}

# Go back to previous directory
cd ${DIR}

# Download required dependencies
python3 -m pip install \
    transforms3d

# Download ROS packages
sudo apt update
sudo apt install -y \
    ros-$ROS_DISTRO-ros2-control \
    ros-$ROS_DISTRO-ros2-controllers \
    ros-$ROS_DISTRO-control-toolbox \
    ros-$ROS_DISTRO-controller-interface \
    ros-$ROS_DISTRO-controller-manager \
    ros-$ROS_DISTRO-position-controllers \
    ros-$ROS_DISTRO-velocity-controllers \
    ros-$ROS_DISTRO-effort-controllers \
    ros-$ROS_DISTRO-joint-trajectory-controller \
    ros-$ROS_DISTRO-joint-group-impedance-controller \
    ros-$ROS_DISTRO-joint-state-publisher \
    ros-$ROS_DISTRO-joint-state-publisher-gui \
    ros-$ROS_DISTRO-joint-state-broadcaster \
    ros-$ROS_DISTRO-joint-limits \
    ros-$ROS_DISTRO-robot-controllers \
    ros-$ROS_DISTRO-robot-controllers-interface \
    ros-$ROS_DISTRO-robot-state-publisher \
    ros-$ROS_DISTRO-hardware-interface \
    ros-$ROS_DISTRO-transmission-interface \
    ros-$ROS_DISTRO-urdf \
    ros-$ROS_DISTRO-urdf-launch \
    ros-$ROS_DISTRO-xacro \
    ros-$ROS_DISTRO-std-msgs \
    ros-$ROS_DISTRO-geometry-msgs \
    ros-$ROS_DISTRO-sensor-msgs \
    ros-$ROS_DISTRO-nav-msgs \
    ros-$ROS_DISTRO-trajectory-msgs \
    ros-$ROS_DISTRO-tf2-geometry-msgs \
    ros-$ROS_DISTRO-tf2-ros \
    ros-$ROS_DISTRO-tf2 \
    ros-$ROS_DISTRO-tf-transformations \
    ros-$ROS_DISTRO-joy-linux \
    ros-$ROS_DISTRO-launch \
    ros-$ROS_DISTRO-launch-ros

# Install Gazebo Fortress with binaries
sudo apt install -y \
    ros-$ROS_DISTRO-ros-gz \
    ros-$ROS_DISTRO-ign-ros2-control \
    ros-$ROS_DISTRO-ign-ros2-control-demos

# Install Navigation package
sudo apt install -y \
    ros-$ROS_DISTRO-navigation2 \
    ros-$ROS_DISTRO-nav2-bringup \
    ros-$ROS_DISTRO-nav2-map-server \
    ros-$ROS_DISTRO-nav2-lifecycle-manager \
    ros-$ROS_DISTRO-slam-toolbox \
    ros-$ROS_DISTRO-rmw-cyclonedds-cpp

echo export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp >> ~/.bashrc
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

# Install Each library
sudo apt install -y \
    mpg321 \
    zenity

# Set up environment variables
echo "" >> /home/$USERNAME/.bashrc
echo "# NekoMimi Bot environment variables" >> /home/$USERNAME/.bashrc
echo "export FTC_SL_PORT=`realpath /dev/serial/by-id/usb-1a86_USB_Serial-if00-port0`" >> /home/$USERNAME/.bashrc
echo "export LDS_SL_PORT=`realpath /dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0`" >> /home/$USERNAME/.bashrc
echo "" >> /home/$USERNAME/.bashrc
source /home/$USERNAME/.bashrc


# # Reload udev rules
sudo udevadm control --reload-rules

# # Trigger the new rules
sudo udevadm trigger

# Go back to previous directory
cd ${DIR}


echo "╚══╣ Setup: NekoMimi Bot (FINISHED) ╠══╝"