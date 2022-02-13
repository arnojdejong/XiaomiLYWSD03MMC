import json

import paho.mqtt.client as mqtt
from pprint import pprint
from device_list import devices

topic = None

print("nr: creating new instance")
client = mqtt.Client()  # create new instance


def init(config):
    global topic

    if not config:
        return

    nr_config = config.get('node_red')
    if not nr_config:
        return

    broker_address = nr_config.get('broker_address')
    if not broker_address:
        return
    topic = nr_config.get('topic')
    if not broker_address:
        return

    username = nr_config.get('broker_username')
    password = nr_config.get('broker_password')
    if username:
        client.username_pw_set(username, password)

    print("nr: connecting to broker")
    client.connect(broker_address)
    print("nr: connected to broker")
    client.loop_start()


def send(device, values):
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
    client.publish(topic, json.dumps(payload).encode())

