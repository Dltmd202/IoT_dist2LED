import RPi.GPIO as gpio
import time
import paho.mqtt.client as mqtt
import json


class Distance:
    def __init__(self, is_person=False, distance=0., trig_pin=13, echo_pin=19, pir=20):
        self.is_person = is_person
        self.distance = distance
        self.trig_pin = trig_pin
        self.echo_pin = echo_pin
        self.pir_pin = pir
        self.client = self.get_client()
        self.gpio_init()

    def gpio_init(self):
        gpio.setmode(gpio.BCM)
        gpio.setup(self.trig_pin, gpio.OUT)
        gpio.setup(self.echo_pin, gpio.IN)
        gpio.setup(self.pir_pin, gpio.OUT)

    def get_client(self):
        client = mqtt.Client()

        def on_connect(client, userdata, flags, rc):
            print("connected with result code " + str(rc))
            client.subscribe("server/distance")

        def on_publish(client, userdata, mid):
            msg_id = mid

        client.on_connect = on_connect
        client.on_publish = on_publish
        return client

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
            return distance
        except KeyboardInterrupt:
            gpio.cleanup()

    def get_person(self):
        gpio.output(self.pir_pin, True)
        time.sleep(1)

        res = gpio.output(self.pir_pin, False)
        time.sleep(1)
        return res

    def res_or_distance(self):
        res = self.get_person()
        if res:
            return (res, self.get_distance())
        else:
            return (res, 0.)

    def run(self, kwargs=["localhost"]):
        self.client.connect(**kwargs)
        self.client.loop_start()

        try:
            while True:
                (res, distance) = self.res_or_distance()
                msg = {
                    "res": res,
                    "distance": distance
                }
                self.client.publish("service/distance", json.dumps(msg))
                print("publishing {msg}")
                time.sleep(3)
        except KeyboardInterrupt:
            print("Finished")
            self.client.loop_stop()
            self.client.disconnect()


if __name__ == '__main__':
    distance = Distance()
    distance.run()
