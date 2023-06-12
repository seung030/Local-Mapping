import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan, PointCloud
from std_msgs.msg  import Header
from rclpy.qos import QoSProfile, QoSDurabilityPolicy, QoSReliabilityPolicy
import math

from std_msgs.msg import Int8MultiArray


import numpy as np
import time
import sys
from lidarlidar.msg import StampedArray

class LidarSubPub(Node):
    def __init__(self):
        super().__init__("lidar_subscriber")
        self.get_logger().info('starting lidar subscription')
        qos = QoSProfile(depth=10)
        qos.reliability = QoSReliabilityPolicy.BEST_EFFORT
        qos.durability = QoSDurabilityPolicy.VOLATILE

        self.scan_sub_handler = self.create_subscription(LaserScan,'scan',self.scan_sub_callback, qos)
        self.publisher_localmap = self.create_publisher(StampedArray,'localmap', qos)

    def scan_sub_callback(self, data):

        angle_increment = data.angle_increment
        angle = data.angle_min

        published_data = StampedArray()
        published_data.stamp.sec = 99
        published_data.stamp.nanosec = 88
        published_data.array = [ 1, 2, 3, 4]
        
        self.publisher_localmap.publish(published_data)
        self.get_logger().info("array:{0}, time_sec:{1}, time_nsec:{2}".format(published_data.stamp.sec, published_data.stamp.nanosec, published_data.array))



def main(args=None):
    rclpy.init(args=args)
    node = LidarSubPub()


    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Keyboard Interrupt (SIGINT)')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
	main()

