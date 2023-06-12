# Local-Mapping
Development of guidance robot technology for the visually impaired

# 센서 데이터 획득 방법 구현
publisher 노드가 발행(publish)하는 센서 데이터를 포함하고 있는 토픽을 수신함으로써 센서 데이터를 응용 프로그램에서 활용할 수 있음
Lidar 센서 데이터는 '/scan' 토픽을 위한 subscriber 노드를 작성하여 수신할 수 있음
Lidar 센서 데이터 토픽을 위한 QosProfile 설정은 필수
-  qos_profile.reliability = QosReliabilityPoilcy.BEST_EFFORT
-  qos_profile.durability = QosDurabilityPoilcy.VOLATILE
Lidar 센서 데이터 토픽 수신을 위한 subscriber 샘플 코드 :
1. rolpy.init()
2. node 생성 : rolpy.create_node() 또는 Node 상속 객체 생성
3. subcriber 생성 : node.create_subscription() 이용
4. --> 이때 토픽 수신되면 호출할 callback 등록
5. 토픽 수신 : 등록된 callback 자동 호출
6. node 제거 : node.destorpy_node()
7. rolpy.shutdown()
