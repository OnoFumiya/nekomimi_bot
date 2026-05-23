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
    "tts_ros"
    "stt_ros"
    "2d_lidar_person_detection"
    "gazebo_worlds"
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


# Additional packages for navigation of TeamSOBITS repository
sobits_packages=(
    "flex_nav"
    "explore_ros2"
)
check_packages=(
    "flex_nav"
    "explore_lite"
)

# clone packages from TeamSOBITS (if not exist)
for ((i = 0; i < ${#sobits_packages[@]}; i++)) {
    if ros2 pkg list 2>/dev/null | grep -q "^${check_packages[i]}$"; then
        echo "${check_packages[i]} is exist. Skipping cloning and installation."
    else
        echo "Clonning: ${sobits_packages[i]}"
        git clone -b $ROS_DISTRO-devel https://github.com/TeamSOBITS/${sobits_packages[i]}.git

        # Check if install.sh exists in each package
        if [ -f ${sobits_packages[i]}/install.sh ]; then
            echo "Running install.sh in ${sobits_packages[i]}."
            cd ${sobits_packages[i]}
            bash install.sh
            cd ..
        fi
    fi
}

# Go back to previous directory
cd ${DIR}

# Install audio packages
bash audio.sh

# Download required dependencies
python3 -m pip install --break-system-packages \
    transforms3d

# Download ROS packages
sudo apt-get update
sudo apt-get install -y \
    ros-$ROS_DISTRO-ros2-control \
    ros-$ROS_DISTRO-ros2-controllers \
    ros-$ROS_DISTRO-control-msgs \
    ros-$ROS_DISTRO-control-toolbox \
    ros-$ROS_DISTRO-controller-interface \
    ros-$ROS_DISTRO-controller-manager \
    ros-$ROS_DISTRO-controller-manager-msgs \
    ros-$ROS_DISTRO-position-controllers \
    ros-$ROS_DISTRO-velocity-controllers \
    ros-$ROS_DISTRO-effort-controllers \
    ros-$ROS_DISTRO-joint-trajectory-controller \
    ros-$ROS_DISTRO-joint-state-publisher \
    ros-$ROS_DISTRO-joint-state-publisher-gui \
    ros-$ROS_DISTRO-joint-state-broadcaster \
    ros-$ROS_DISTRO-joint-limits \
    ros-$ROS_DISTRO-robot-state-publisher \
    ros-$ROS_DISTRO-hardware-interface \
    ros-$ROS_DISTRO-transmission-interface \
    ros-$ROS_DISTRO-urdf \
    ros-$ROS_DISTRO-urdf-launch \
    ros-$ROS_DISTRO-xacro \
    ros-$ROS_DISTRO-moveit \
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
    ros-$ROS_DISTRO-launch-ros \
    ros-$ROS_DISTRO-gz-ros2-control \
    ros-$ROS_DISTRO-actuator-msgs \
    ros-$ROS_DISTRO-gps-msgs \
    ros-$ROS_DISTRO-ros-gz-bridge \
    ros-$ROS_DISTRO-ros-gz-sim \
    ros-$ROS_DISTRO-ros-gz-interfaces \
    ros-$ROS_DISTRO-usb-cam

# Set up the environment
sudo usermod -aG dialout $USERNAME

# Install Gazebo Harmonic with binaries
sudo apt-get update
sudo apt-get install -y \
    curl \
    mpg321 \
    lsb-release \
    gnupg \
    acpi

sudo curl https://packages.osrfoundation.org/gazebo.gpg --output /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] http://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/gazebo-stable.list > /dev/null
sudo apt-get update
sudo apt-get install -y \
    gz-harmonic

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
    zenity \
    xterm

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
