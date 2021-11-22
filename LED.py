import json
import RPi.GPIO as gpio
import paho.mqtt.client as mqtt

class LedController:
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

    def gpio_init(self):
        gpio.setmode(gpio.BCM)
        gpio.setup(self.led_red, gpio.OUT)
        gpio.setup(self.led_green, gpio.OUT)
        gpio.setup(self.led_blue, gpio.OUT)

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

    def run_led(self):
        gpio.output(self.led_red, self.red_status)
        gpio.output(self.led_green, self.green_status)
        gpio.output(self.led_blue, self.blue_status)


    def distance_dealing(self, msg):
        distance_info = json.loads(msg.payload)
        self.distance = distance_info['distance']
        self.red_status = distance_info['red']
        self.green_status = distance_info['green']
        self.blue_status = distance_info['blue']

    def run(self):
        self.client.connect("localhost")
        try:
            self.client.loop_forever()
        except KeyboardInterrupt:
            print("Finished!")
            self.client.unsubscribe("control/led")
            self.client.disconnect()


if __name__ == '__main__':
    led = LedController()
    led.run()
