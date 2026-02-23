import time
import numpy as np
import os

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import PoseStamped, Point, Twist
from std_srvs.srv import SetBool

from rclpy.qos import QoSProfile, QoSDurabilityPolicy, QoSReliabilityPolicy, QoSHistoryPolicy


class VelocityFollower(Node):
    def __init__(self):
        super().__init__('velocity_follower')
        self.velocity_topic = self.declare_parameter("velocity_topic", "/nekomimi_bot/cmd_vel").value
        self.timeout_sec = self.declare_parameter("timeout_sec", 0.3).value
        self.max_linear_vel = self.declare_parameter("max_linear_vel", 0.15).value
        self.max_angular_vel = self.declare_parameter("max_angular_vel", 0.4).value
        self.publish_rate = self.declare_parameter("publish_rate", 10).value
        self.detect_mode = self.declare_parameter("execute_default", True).value

        self.pt = Point()
        self.get_time = time.time()
        self.vel = Twist()

        self.last_pub_flag = False

        qos_policy = rclpy.qos.QoSProfile(
            # reliability=rclpy.qos.ReliabilityPolicy.RELIABLE,
            reliability=rclpy.qos.ReliabilityPolicy.BEST_EFFORT,
            history=rclpy.qos.HistoryPolicy.KEEP_LAST,
            depth=1
        )

        # Publisher
        self._vel_pub = self.create_publisher(
            Twist, self.velocity_topic, 1,
        )

        # Subscriber
        self._point_sub = self.create_subscription(
            PoseStamped, "following_point", self._point_callback, qos_policy,
        )

        # Service
        self._run_ctrl_srv = self.create_service(
            SetBool, "follower/velocity/run_ctr", self._run_ctrl_callback
        )

        self.timer = self.create_timer(1.0/float(self.publish_rate), self._timer_callback)

    def _run_ctrl_callback(self, request, response):
        if ((request.data == True) or (request.data == False)):
            response.success = True
            self.detect_mode = request.data
        else:
            response.success = False
            self.detect_mode = False

        return response

    def _point_callback(self, msg):
        self.pt = msg.pose.position
        self.get_time = time.time()

    def _timer_callback(self):
        if ((not self.detect_mode) and (self.last_pub_flag)): return

        if ((time.time() - self.get_time) < self.timeout_sec):
            if (np.sqrt(self.pt.x**2 + self.pt.y**2) < 1.5):
                if (np.fabs(np.arctan2(self.pt.y, self.pt.x)) < 0.2):
                    self.vel.angular.z = 0.0
                else:
                    if (self.max_angular_vel < np.fabs(np.arctan2(self.pt.y, self.pt.x))):
                        self.vel.angular.z = self.max_angular_vel
                    else:
                        self.vel.angular.z = np.arctan2(self.pt.y, self.pt.x)
                self.vel.linear.x = 0.0
            elif (np.sqrt(self.pt.x**2 + self.pt.y**2) < 2.0):
                if (self.max_linear_vel < np.sqrt(self.pt.x**2 + self.pt.y**2)):
                    self.vel.linear.x = self.max_linear_vel
                else:
                    self.vel.linear.x = np.sqrt(self.pt.x**2 + self.pt.y**2)

                if (np.fabs(np.arctan2(self.pt.y, self.pt.x)) < 0.2):
                    self.vel.angular.z = 0.0
                else:
                    if (self.max_angular_vel < np.fabs(np.arctan2(self.pt.y, self.pt.x))):
                        self.vel.angular.z = self.max_angular_vel
                    else:
                        self.vel.angular.z = np.arctan2(self.pt.y, self.pt.x)
            else:
                self.vel.linear.x = 0.0
                self.vel.angular.z = 0.0
            self._vel_pub.publish(self.vel)
        else:
            self._vel_pub.publish(Twist())

        self.last_pub_flag = False

        if (not self.detect_mode):
            self.last_pub_flag = True
            self._vel_pub.publish(Twist())



def main(args=None):
    rclpy.init(args=args)
    node = VelocityFollower()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()