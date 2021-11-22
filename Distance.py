import RPi.GPIO as gpio
import time
import paho.mqtt.client as mqtt
import json


class Distance:

    # 인체 감지 및 거리 센서 객체
    # 해당 어플리케이션의 객체 생성에 인자를 줄 수 있도록하여
    # 오작동이 생겨 다시 작동하더라도 상태를 바로 업데이트할 수 있도록 하였습니다.
    def __init__(self, is_person=False, distance=0., trig_pin=13, echo_pin=19, pir=20):
        self.is_person = is_person
        self.distance = distance
        self.trig_pin = trig_pin
        self.echo_pin = echo_pin
        self.pir_pin = pir
        self.client = self.get_client()
        self.gpio_init()


    # gpio핀을 초기화 하는 메서드
    # 트리거 핀을 ouput으로 설정
    # 에코 핀을 input으로 설정
    # PIR 센서 핀을 input으로 설정
    def gpio_init(self):
        gpio.setmode(gpio.BCM)
        gpio.setup(self.trig_pin, gpio.OUT)
        gpio.setup(self.echo_pin, gpio.IN)
        gpio.setup(self.pir_pin, gpio.IN)


    # mqtt 클라이언트 멤버를 반환
    # on_connect, on_publish 콜백함수가 지정된
    # mqtt 클라이언트 객체를 반환합니다.
    def get_client(self):
        client = mqtt.Client()

        # sensor/distance 토픽에 구독 콜백 메서드
        def on_connect(client, userdata, flags, rc):
            print("connected with result code " + str(rc))
            client.subscribe("sensor/distance")

        def on_publish(client, userdata, mid):
            msg_id = mid

        client.on_connect = on_connect
        client.on_publish = on_publish
        return client

    # 거리를 센싱하는 메서드
    # 센싱 중 KeyboardInterrput 얘외를 캐치해 준다.
    # 트리거핀을 출력을 보정하고 출력을 준다.
    # 에코핀의 출력이 0부터 1로 바뀔 때까지의 타임객체를 기록한다.
    # 거리 = 속력 * 시간 음속을 이용해 거리를 구하고
    # 해당 거리는 왕복된 거리임으로 반을 나누어 준다.
    def get_distance(self):
        try:
            while True:
                gpio.output(self.trig_pin, False)
                time.sleep(1)
                gpio.output(self.trig_pin, True)
                time.sleep(0.00001)
                gpio.output(self.trig_pin, False)

                while gpio.input(self.echo_pin) == 0:
                    pulse_start = time.time()
                while gpio.input(self.echo_pin) == 1:
                    pulse_end = time.time()
                pulse_duration = pulse_end - pulse_start
                distance = pulse_duration * 34000 / 2
                distance = round(distance, 2)
                self.distance = distance
                return distance
        except KeyboardInterrupt:
            distance = 0
            gpio.cleanup()

    # 인체 감지 메서드
    # pir 핀의 입력이 True인지 검사
    def get_person(self):
        return gpio.input(self.pir_pin) == True

    # 사용자의 사용편의성을 위해 모든 기능을 캡슐화하여 run 메서드에 묶어 두었습니다.
    # 해당 메서드는 해당 UDP/IP 에 접속한 후
    # 토픽에 대한 메세지를 listening 합니다.
    # 키보드 인터럽트 에러가 나타날시 구독을 해제하고
    # 해당 UDP/IP 에 접속을 해제합니다.
    def run(self, kwargs=["localhost"]):
        self.client.connect("localhost")
        self.client.loop_start()

        try:
            while True:
                is_person = self.get_person()
                distance = self.get_distance()
                msg = {
                    "is_person": is_person,
                    "distance": distance
                }
                if not is_person:
                    msg['distance'] = 10000
                self.client.publish("sensor/distance", json.dumps(msg))
                print(f"publishing {msg}")
                time.sleep(0.3)
        except KeyboardInterrupt:
            print("Finished")
            self.client.loop_stop()
            self.client.disconnect()


# 해당 프로그램을 임포트해서도 사용할 수 있도록
# 해당 파일이 메인으로 실행될 때만 바로 작동되도록 하였습니다.
if __name__ == '__main__':
    distance = Distance()
    distance.run()
