# import time
import numpy as np
import os

import rclpy
from rclpy.node import Node

from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from geometry_msgs.msg import PoseStamped, PoseArray, Pose, Point
from std_srvs.srv import SetBool

from rclpy.qos import QoSProfile, QoSDurabilityPolicy, QoSReliabilityPolicy, QoSHistoryPolicy


class PanTiltFollower(Node):
    def __init__(self):
        super().__init__('pantilt_follower')
        self.human_pose_topic = self.declare_parameter("human_pose_topic", "dr_spaam_detections").value
        self.joint_topic      = self.declare_parameter("joint_topic", "joint_trajectory_controller/joint_trajectory").value
        self.pan_joint        = self.declare_parameter("pan_joint", "head_pan_joint").value
        self.tilt_joint       = self.declare_parameter("tilt_joint", "head_tilt_joint").value
        self.use_rollpitchyaw = self.declare_parameter("use_rollpitchyaw", False).value
        self.detect_mode      = self.declare_parameter("execute_default", True).value

        self.jt = JointTrajectory()
        self.jt.joint_names = [self.pan_joint, self.tilt_joint]

        qos_policy = rclpy.qos.QoSProfile(
            # reliability=rclpy.qos.ReliabilityPolicy.RELIABLE,
            reliability=rclpy.qos.ReliabilityPolicy.BEST_EFFORT,
            history=rclpy.qos.HistoryPolicy.KEEP_LAST,
            depth=1
        )

        # Publisher
        self._joint_pub = self.create_publisher(
            JointTrajectory, self.joint_topic, 1,
        )
        self._pt_pub = self.create_publisher(
            PoseStamped, "following_point", 1,
        )

        # Subscriber
        self._pose_sub = self.create_subscription(
            PoseArray, self.human_pose_topic, self._pose_callback, qos_policy,
        )

        # Service
        self._run_ctrl_srv = self.create_service(
            SetBool, "follower/pantilt/run_ctr", self._run_ctrl_callback
        )

    def _run_ctrl_callback(self, request, response):
        if ((request.data == True) or (request.data == False)):
            response.success = True
            self.detect_mode = request.data
        else:
            response.success = False
            self.detect_mode = False

        return response

    def _pose_callback(self, msg):
        if not self.detect_mode: return

        self.jt.header = msg.header

        best_pt = Point()
        dist_thresh = float("inf")
        dist = dist_thresh
        for pt in msg.poses:
            if (np.sqrt(pt.position.x**2 + pt.position.y**2) < dist):
                dist = np.sqrt(pt.position.x**2 + pt.position.y**2)
                best_pt = pt.position

        if (dist != dist_thresh):

            pan = np.arctan2(best_pt.y, best_pt.x)
            tilt = -np.arctan2(1.4, dist) if self.use_rollpitchyaw else np.arctan2(1.4, dist)

            self.jt.points = [JointTrajectoryPoint()]
            self.jt.points[0].positions = [pan, tilt]
            # self.jt.points[0].time_from_start.sec = 1
            self.jt.points[0].time_from_start.nanosec = int(0.5 * (10**9))

            self._pt_pub.publish(PoseStamped(header=msg.header, pose=Pose(position=best_pt)))
            self._joint_pub.publish(self.jt)



def main(args=None):
    rclpy.init(args=args)
    node = PanTiltFollower()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()