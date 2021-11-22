import json
import paho.mqtt.client as mqtt

class ServerApplication:
    # 브로커 서버 응용프로그램
    # 해당 어플리케이션의 객체 생성에 인자를 줄 수 있도록하여
    # 오작동이 생겨 다시 작동하더라도 상태를 바로 업데이트할 수 있도록 하였습니다.
    def __init__(self, is_person=False, distance=0., status=None):
        self.client = self.getClient()
        self.is_person = is_person
        self.distance = distance
        self.status = status


    # mqtt 클라이언트 멤버를 반환
    # on_connect, on_publish 콜백함수가 지정된
    # mqtt 클라이언트 객체를 반환합니다.
    def getClient(self):
        client = mqtt.Client()

        def on_connect(client, userdata, flags, rc):
            print("connected with result code " + str(rc))
            client.subscribe("sensor/distance")
            client.subscribe("control/led")

        def on_message(client, userdata, msg):
            print(f"[{msg.topic}] Get Message: {msg.payload}")
            if msg.topic == 'sensor/distance':
                self.distance_dealing(msg)
            self.led_control(msg)

        client.on_connect = on_connect
        client.on_message = on_message
        return client

    # Distance 객체에서 Publish 된 메세지 파싱
    # json 파일을 파싱하여 거리 정보와 인체 탐자 유무 정보의 인스턴스 멤버를 update 합니다.
    def distance_dealing(self, msg):
        distance_info = json.loads(msg.payload)
        self.distance = float(distance_info['distance'])
        self.is_person = distance_info['is_person']

    # 거리와 인체 유무 정보의 멤러를 기반으로 동작하는 led 제거 메서드
    # 거리와 인체 유무를 바탕으로 메세지를 작성합니다.
    # 서버를 상태를 유지하지 않도록하는 방식으로 작동하기 위해
    # string[색깔]: Bool[작동여부]의 key: value로 매핑하여 작성
    # 확장성을 위해 현재 온도와 손님의 수 정보를 묶어 Json으로 파싱하여 Pulish
    def led_control(self, msg):
        status = None
        msg = {
            "distance": self.distance,
            "green": False,
            "red": False,
            "blue": False,
        }
        if self.distance <= 20:
            msg["red"] = True
            status = "red"
        elif 20 < self.distance <= 40:
            msg["green"] = True
            status = "green"
        elif 40 < self.distance < 10000:
            msg["blue"] = True
            status = "blue"
        if not self.status or self.status != status:
            self.status = status
            self.client.publish("control/led", json.dumps(msg))


    # 사용자의 사용편의성을 위해 모든 기능을 캡슐화하여 run 메서드에 묶어 두었습니다.
    # 해당 메서드는 해당 UDP/IP 에 접속한 후
    # 토픽에 대한 메세지를 listening 합니다.
    # 키보드 인터럽트 에러가 나타날시 구독을 해제하고
    # 해당 UDP/IP 에 접속을 해제합니다.
    def run(self, kwargs=["localhost"]):
        self.client.connect(*kwargs)
        try:
            self.client.loop_forever()
        except KeyboardInterrupt:
            print("Finished!")
            self.client.unsubscribe("sensor/distance")
            self.client.unsubscribe("control/led")
            self.client.disconnect()


# 해당 프로그램을 임포트해서도 사용할 수 있도록
# 해당 파일이 메인으로 실행될 때만 바로 작동되도록 하였습니다.
if __name__ == '__main__':
    service = ServerApplication()
    service.run()