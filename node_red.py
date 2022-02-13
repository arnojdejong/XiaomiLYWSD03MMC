import json

import paho.mqtt.client as mqtt
from pprint import pprint
from device_list import devices

topic = None


class NodeRed:
    def __init__(self):
        self.client = None
        self.broker_address = None
        self.username = None
        self.password = None
        self.topic = None

    def init(self, config):
        if not config:
            return

        nr_config = config.get('node_red')
        if not nr_config:
            return

        print("nr: creating new instance")
        self.client = mqtt.Client()  # create new instance

        self.broker_address = nr_config.get('broker_address')
        if not self.broker_address:
            return

        self.topic = nr_config.get('topic')
        if not self.broker_address:
            return

        self.username = nr_config.get('broker_username')
        self.password = nr_config.get('broker_password')
        if self.username:
            self.client.username_pw_set(self.username, self.password)

    def start(self):
        print("nr: start")
        if not self.broker_address:
            return

        print("nr: connecting to broker")
        self.client.connect(self.broker_address)
        print("nr: connected to broker")
        self.client.loop_start()

    def send(self, device, values):
        if not topic:
            return

        address = ':'.join('{:02x}'.format(x) for x in values.address)

        payload = {
            "type": "Xiaomi LYWSD03MMC",
            "location": devices[values.address]["name"],
            "address": address,
            "temperature_celcius": values.temperature,
            "humidity": values.humidity,
            "battery_level": values.battery_level,
            "battery_voltage": values.battery_voltage,
            "frame_count": values.frame,
            "rssi": device.rssi
        }
        pprint(payload)
        print("Publishing message to topic", topic)
        self.client.publish(topic, json.dumps(payload).encode())

