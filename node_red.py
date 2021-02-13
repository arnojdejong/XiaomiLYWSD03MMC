import json

import paho.mqtt.client as mqtt  # import the client1
from pprint import pprint
from device_list import devices

topic = "test/in"

broker_address = "station"
# broker_address="iot.eclipse.org"
print("creating new instance")
client = mqtt.Client("PyXiaomiBLE")  # create new instance
print("connecting to broker")
client.connect(broker_address)  # connect to broker


def send(device, values):
    payload = {
        "type": "Xiaomi LYWSD03MMC",
        "location": devices[values.address]["name"],
        "address": values.address,
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

