import json
import paho.mqtt.client as mqtt

class ServerApplication:
    def __init__(self, is_person=False, distance=0., led_red=False,
                 led_green=False, led_blue=False):
        self.client = self.getClient()
        self.is_person = is_person
        self.distance = distance
        self.led_red = led_red
        self.led_green = led_green
        self.led_blue = led_blue
        self.leds = [self.led_red, self.led_green, self.led_blue]
        self.working_led = None


    def getClient(self):
        client = mqtt.Client()

        def on_connect(client, userdata, flags, rc):
            print("connected with result code " + str(rc))
            client.subscribe("service/distance")
            client.subscribe("service/led")

        def on_message(client, userdata, msg):
            print(f"[{msg.topic}] Get Message: {str(msg.payload)}")
            if msg.topic == 'service/distance':
                self.distance_dealing(msg)
            self.led_control()

        client.on_connect = on_connect
        client.on_message = on_message
        return client

    def distance_dealing(self, msg):
        distance_info = json.loads(msg.payload)
        self.distance = int(distance_info['distance'])

    def led_control(self, msg):
        will_work = 0
        if self.distance >= 40:
            will_work = self.led_blue
        elif self.distance >= 20:
            will_work = self.led_green
        else:
            will_work = self.led_red
        if self.working_led != will_work:
            msg = {
                "distance": self.distance,
                "before_led": self.working_led,
                "after_led": will_work
            }
            self.client.publish("service/led", json.dumps(msg))
            self.working_led = will_work


    def run(self, kwargs=["localhost"]):
        self.client.connect(*kwargs)
        try:
            self.client.loop_forever()
        except KeyboardInterrupt:
            print("Finished!")
            self.client.unsubscribe("service/#")
            self.client.disconnect()


if __name__ == '__main__':
    service = ServerApplication()
    service.run()