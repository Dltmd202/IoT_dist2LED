import json
import paho.mqtt.client as mqtt

class ServerApplication:
    def __init__(self, is_person=False, distance=0., led_red=False,
                 led_green=False, led_blue=False):
        self.client = self.getClient()
        self.is_person = is_person
        self.distance = distance
        self.status = None
        self.working_led = None


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
            if self.is_person:
                self.led_control(msg)

        client.on_connect = on_connect
        client.on_message = on_message
        return client

    def distance_dealing(self, msg):
        distance_info = json.loads(msg.payload)
        self.distance = float(distance_info['distance'])
        self.is_person = distance_info['is_person']

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
        elif 40 < self.distance:
            msg["blue"] = True
            status = "blue"
        if not self.status or self.status != status:
            self.status = status
            self.client.publish("control/led", json.dumps(msg))



    def run(self, kwargs=["localhost"]):
        self.client.connect(*kwargs)
        try:
            self.client.loop_forever()
        except KeyboardInterrupt:
            print("Finished!")
            self.client.unsubscribe("sensor/distance")
            self.client.unsubscribe("control/led")
            self.client.disconnect()


if __name__ == '__main__':
    service = ServerApplication()
    service.run()