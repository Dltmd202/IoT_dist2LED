import json

import paho.mqtt.client as mqtt

class LedController:
    def __init__(self, led_red=22, led_green=27, led_blue=17):
        self.client = self.getClient()
        self.onLight = None
        self.distance = None
        self.before_led = None
        self.after_led = None
        self.led_red = led_red
        self.led_green = led_green
        self.led_blue = led_blue
        self.will_work = None
        self.before_led = None
        self.gpio_init()

    def gpio_init(self):
        gpio.setmode(gpio.BCM)
        gpio.setup(self.led_red, gpio.OUT)
        gpio.setup(self.led_green, gpio.OUT)
        gpio.setup(self.led_blue, gpio.OUT)

    def getClient(self):
        client = mqtt.Client()

        def on_connect(client, userdata, flags, rc):
            print("connected with result code " + str(rc))
            client.subscribe("service/led")

        def on_message(client, userdata, msg):
            print(f"[{msg.topic}] Get Message: {str(msg.payload)}")
            self.distance_dealing(msg)
            self.run_led()

        client.on_connect = on_connect
        client.on_message = on_message
        return client

    def run_led(self):
        gpio.output(self.before_led, False)
        gpio.output(self.will_work, True)


    def distance_dealing(self, msg):
        distance_info = json.loads(msg.payload)
        self.distance = distance_info['distance']
        self.before_led = distance_info['before_led']
        self.after_led = distance_info['after_led']

    def run(self):
        self.client.connect("localhost")
        try:
            self.client.loop_forever()
        except KeyboardInterrupt:
            print("Finished!")
            self.client.unsubscribe("service/#")
            self.client.disconnect()


if __name__ == '__main__':
    led = LedController()
    led.run()