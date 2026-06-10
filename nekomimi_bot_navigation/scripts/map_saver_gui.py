#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import os
from subprocess import Popen, PIPE
import time

def save_map_command(node):
    proc = Popen(["zenity", "--file-selection", "--save", "--confirm-overwrite", "--filename=/home/" + str(os.getenv("USERNAME")) + "/colcon_ws/src/nekomimi_bot/nekomimi_bot_navigation/map/map_example.yaml"],
        stdout=PIPE,
        shell=False)
    out, err = proc.communicate()
    if (str(out.decode('utf-8')) == ""):
        print("\033[91m\033[05mNONE FILE PATH\033[0m")
        node.get_logger().info('\033[91m\033[05mNONE FILE PATH\033[0m')
        return False, ""
    else:
        if (len(out.decode('utf-8').split("."))==1):
            path = ".".join(out.decode('utf-8').split("."))
        else:
            path = ".".join(out.decode('utf-8').split(".")[:-1])
        path = path.replace("\n", "")
        print("MAP FILE :\033[93m\033[05m", path, "\033[0m")
        node.get_logger().info('MAP FILE :\033[93m\033[05m'+path+'\033[0m')
        return True, path


def main(args=None):
    rclpy.init(args=args)
    node = Node("map_saver_gui")
    while rclpy.ok():
        r, path = save_map_command(node)
        if r:
            Popen(["ros2", "run", "nav2_map_server", "map_saver_cli", "-f", path])
    node.execute()
    rclpy.shutdown()

if __name__ == '__main__':
    main()