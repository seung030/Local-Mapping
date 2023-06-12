import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan, PointCloud
from geometry_msgs.msg import Point32
from std_msgs.msg  import Header
from rclpy.qos import QoSProfile, QoSDurabilityPolicy, QoSReliabilityPolicy
import math
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from std_msgs.msg import Int8MultiArray
from std_msgs.msg import Int32MultiArray
import builtin_interfaces
from rclpy.clock import ClockType
from rclpy.duration import Duration
from rclpy.impl.implementation_singleton import rclpy_implementation as _rclpy
import numpy as np
import time
import sys
from lidarlidar.msg import StampedArray

#"scan" 토픽의 라이다 데이터를 읽어 좌표평면의 데이터로 변환하여 "scan_points" 토픽으로 publishing 
#자신이 publishing 하는 "sc+an_points" 토픽을 읽어 좌표평면 데이터 배열의 첫 번째 데이터의 x, y 값을 출력 

class LidarSubPub(Node):
	def __init__(self):
		super().__init__("lidar_subscriber")
		self.get_logger().info('starting lidar subscription')
		qos = QoSProfile(depth=10)
		qos.reliability = QoSReliabilityPolicy.BEST_EFFORT
		qos.durability = QoSDurabilityPolicy.VOLATILE

		self.scan_points_pub_handler = self.create_publisher(PointCloud, "scan_points", 10)	#토픽의 데이터 타입, 토픽 이름, QoS 설정을 입력받음
		self.scan_sub_handler = self.create_subscription(LaserScan,'scan',self.scan_sub_callback, qos)
		self.points_sub_handler = self.create_subscription(PointCloud, "scan_points", self.points_sub_callback, 10)
		self.publisher_localmap = self.create_publisher(StampedArray,'localmap', qos)
		# self.timer = self.create_timer(0.5 , self.points_sub_handler)
		

	#새로운 데이터가 수신되면 지정한 콜백이 실행
	#이때 토픽의 데이터는 콜백의 두 번째 인자 값으로 넘겨주게 됨
	#두 번째 매개변수인 data에 토픽의 데이터가 들어감
	def scan_sub_callback(self, data):
		pointcloud_msg = PointCloud()
		pointcloud_msg.header.stamp = self.get_clock().now().to_msg() #nsec
		pointcloud_msg.header.frame_id = "laser_frame"

		angle_increment = data.angle_increment
		angle = data.angle_min	#측정 데이터의 시작점
		
		# 각도, 거리 -> 좌표 (m단위)
		for point in data.ranges:
			coordinate_x = math.cos(angle) * point
			coordinate_y = math.sin(angle) * point
			angle += angle_increment

			if abs(coordinate_x) == 0 and abs(coordinate_y) == 0:
				continue

			point_msg = Point32()
			point_msg.x = coordinate_x 	#x
			point_msg.y = coordinate_y 	#y
			point_msg.z = float(data.header.stamp.sec)	#timestamp_seconds

			pointcloud_msg.points.append(point_msg)

		self.scan_points_pub_handler.publish(pointcloud_msg)


	#토픽의 데이터는 앞서 확인한 토픽의 데이터구조와 동일
	#매개변수 data에 object 형태로 sensor_msgs/msg/LaserScan가 저장되기 때문에 아래와 같은 방법으로 원하는 데이터에 접근 가능
	#첫 번째 거리 데이터: data.ranges[0]

	

#거리 데이터가 Array로 담긴 data.ranges를 순차적으로 읽으며
#삼각함수를 사용해 X, Y 좌표 데이터로 변환해 PointCloud 형태로 변환한 후
#scan_points_pub_handler를 사용해 scan_points 토픽으로 publish

	def points_sub_callback(self, data):
		for point in data.points:
			oldx = point.x
			oldy = point.y
			if 0 < point.x < 0. and 0 < point.y < 0.5:			#x>0 and y>0
				point.x = point.x-0.05
				point.x = point.x/0.1
				point.x = point.x + 1 + 4
				point.y = point.y-0.05
				point.y= point.y/0.1
				point.y = point.y + 1 - 4
			elif -0.5 < point.x < 0 and 0 < point.y < 0.5:		#x<0 and y>0
				point.x = point.x+0.05
				point.x = point.x/0.1
				point.x = point.x - 1 + 4
				point.y = point.y-0.05
				point.y= point.y/0.1
				point.y = point.y + 1 - 4
				#
			elif 0 < point.x < 0.5 and -0.5 < point.y < 0 :		#x>0 and y<0
				point.x = point.x-0.05
				point.x = point.x/0.1
				point.x = point.x + 1 + 4
				point.y = point.y + 0.05
				point.y = point.y/0.1
				point.y = point.y - 1 - 4
				#+
				#-
			elif -0.5 < point.x < 0 and -0.5 < point.y < 0 :	#x<0 and y<0
				point.x = point.x+0.05
				point.x = point.x/0.1
				point.x = point.x - 1  + 4
				point.y = point.y + 0.05
				point.y = point.y/0.1
				point.y = point.y - 1 - 4
           
			# try:
			# 	self.get_logger().info("x:{0}, y:{1}, oldx:{2}, oldy:{3}, time:{4}".format(int(point.x)+4, int(point.y)-4, oldx, oldy, int(point.z) ))
			# except ValueError:
			# 	pass
			
			nano_sec = data.header.stamp.sec * 1,000,000,000
			nano_sec = nano_sec[0]
			
			# localmap = Int32MultiArray()
			# localmap = [[0 for j in range(9)] for i in range(9)]
			# localmap = np.array(localmap)
			# localmap = np.zeros((9,9), dtype=np.int8)
		# 	localmap = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
		# 0, 0, 0, 0, 0, 0, 0, 0, 0],
		#    [0, 0, 0, 0, 0, 0, 0, 0, 0],
		#    [0, 0, 0, 0, 0, 0, 0, 0, 0],
		#    [0, 0, 0, 0, 0, 0, 0, 0, 0],
		#    [0, 0, 0, 0, 0, 0, 0, 0, 0],
		#    [0, 0, 0, 0, 0, 0, 0, 0, 0],
		#    [0, 0, 0, 0, 0, 0, 0, 0, 0]]
			localmap = [0]*81
			if 0 <= point.x <= 9 and -9 <= point.y <= 0:
				localmap[int(point.x)+int(point.y)*9] = 1
				try:
					self.get_logger().info("array:{0}, time_sec:{1}, time_nsec:{2}".format(localmap, point.z, nano_sec))
					msg = StampedArray()
					msg.stamp = data.header.stamp	#nano_sec 
					msg.array = localmap
					self.publisher_localmap.publish(msg)
				except ValueError:
					pass
			# localmap = [0]*81	#clear......
		self.get_logger().info("{0}".format("hello"))
					

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


