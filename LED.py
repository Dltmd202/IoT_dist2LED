import json

import paho.mqtt.client as mqtt

class LedController:
    def __init__(self):
        self.client = self.get_clent()
        self.onLight = None

    def getClient(self):
        client = mqtt.Client()

        def on_connect(client, userdata, flags, rc):
            print("connected with result code " + str(rc))
            client.subscribe("building/light")

        def on_message(client, userdata, msg):
            print(f"[{msg.topic}] Get Message: {str(msg.payload)}")
            self.lightDealing(msg)
            if self.onLight:
                print("Light On")
            else:
                print("Light Off")

        client.on_connect = on_connect
        client.on_message = on_message
        return client

    def light_dealing(self, msg):
        distance_info = json.loads(msg.payload)
        self.onLight = distance_info['distance']

    def run(self, kwargs=["localhost"]):
        self.client.connect(*kwargs)
        try:
            self.client.loop_forever()
        except KeyboardInterrupt:
            print("Finished!")
            self.client.unsubscribe("building/#")
            self.client.disconnect()


if __name__ == '__main__':
    led = LedController
    led.run()