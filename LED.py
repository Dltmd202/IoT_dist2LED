import json
import RPi.GPIO as gpio
import paho.mqtt.client as mqtt

class LedController:
    # LED 조작 객체
    # 해당 어플리케이션의 객체 생성에 인자를 줄 수 있도록하여
    # 오작동이 생겨 다시 작동하더라도 상태를 바로 업데이트할 수 있도록 하였습니다.
    def __init__(self, led_red=22, led_green=27, led_blue=17):
        self.client = self.getClient()
        self.distance = None
        self.led_red = led_red
        self.led_green = led_green
        self.led_blue = led_blue
        self.red_status = False
        self.green_status = False
        self.blue_status = False
        self.gpio_init()

    # gpio핀을 초기화 하는 메서드
    # 3가지의 led 핀을 ouput으로 설정
    def gpio_init(self):
        gpio.setmode(gpio.BCM)
        gpio.setup(self.led_red, gpio.OUT)
        gpio.setup(self.led_green, gpio.OUT)
        gpio.setup(self.led_blue, gpio.OUT)

    # mqtt 클라이언트 멤버를 반환
    # on_connect, on_message 콜백함수가 지정된
    # mqtt 클라이언트 객체를 반환합니다.
    def getClient(self):
        client = mqtt.Client()

        def on_connect(client, userdata, flags, rc):
            print("connected with result code " + str(rc))
            client.subscribe("control/led")

        def on_message(client, userdata, msg):
            print(f"[{msg.topic}] Get Message: {msg.payload}")
            self.distance_dealing(msg)
            self.run_led()

        client.on_connect = on_connect
        client.on_message = on_message
        return client

    # led의 출력을 관리하는 메서드
    # 메세지를 통해 3개의 led의 상태를 모두 기록함으로
    # 이에 따른 출력으로 동기화해준다.
    def run_led(self):
        gpio.output(self.led_red, self.red_status)
        gpio.output(self.led_green, self.green_status)
        gpio.output(self.led_blue, self.blue_status)

    # 거리 정보를 파싱하는 메서드
    # 현재 거리 정보와 각각의 led 상태정보를 저장한다.
    def distance_dealing(self, msg):
        distance_info = json.loads(msg.payload)
        self.distance = distance_info['distance']
        self.red_status = distance_info['red']
        self.green_status = distance_info['green']
        self.blue_status = distance_info['blue']

    # 사용자의 사용편의성을 위해 모든 기능을 캡슐화하여 run 메서드에 묶어 두었습니다.
    # 해당 메서드는 해당 UDP/IP 에 접속한 후
    # 토픽에 대한 메세지를 listening 합니다.
    # 키보드 인터럽트 에러가 나타날시 구독을 해제하고
    # 해당 UDP/IP 에 접속을 해제합니다.
    def run(self):
        self.client.connect("localhost")
        try:
            self.client.loop_forever()
        except KeyboardInterrupt:
            print("Finished!")
            self.client.unsubscribe("control/led")
            self.client.disconnect()


# 해당 프로그램을 임포트해서도 사용할 수 있도록
# 해당 파일이 메인으로 실행될 때만 바로 작동되도록 하였습니다.
if __name__ == '__main__':
    led = LedController()
    led.run()
