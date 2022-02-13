import json

import paho.mqtt.client as mqtt

print("ha: creating new instance")
client = mqtt.Client()  # create new instance


def init(config):
    if not config:
        return

    ha_config = config.get('home_assistant')
    if not ha_config:
        return

    broker_address = ha_config.get('broker_address')
    if not broker_address:
        return

    username = ha_config.get('broker_username')
    password = ha_config.get('broker_password')
    if username:
        client.username_pw_set(username, password)

    print("ha: connecting to broker")
    client.connect(broker_address)  # connect to broker
    print("ha: connected to broker")
    client.loop_start()


def send_mqtt_temperature_discovery_msg(state_topic, address):
    discovery_topic = "homeassistant/sensor/xiaomi_lywsd03mmc_" + address + "/temperature/config"
    payload = {
        'name': 'xiaomi lywsd03mmc ' + address + ' temperature',
        'unique_id': 'xiaomi_lywsd03mmc_' + address + '_temperature',
        'state_topic': state_topic,
        'unit_of_measurement': '°C',
        'device_class': 'temperature',
        'value_template': '{{value_json.temperature}}',
        'force_update': True,
        'expire_after': 120
    }
    client.publish(discovery_topic, json.dumps(payload).encode())


def send_mqtt_humidity_discovery_msg(state_topic, address):
    discovery_topic = "homeassistant/sensor/xiaomi_lywsd03mmc_" + address + "/humidity/config"
    payload = {
        'name': 'xiaomi lywsd03mmc ' + address + ' humidity',
        'unique_id': 'xiaomi_lywsd03mmc_' + address + '_humidity',
        'state_topic': state_topic,
        'unit_of_measurement': '%',
        'device_class': 'humidity',
        'value_template': '{{ value_json.humidity }}',
        'force_update': True,
        'expire_after': 120
    }
    client.publish(discovery_topic, json.dumps(payload).encode())


def send_mqtt_battery_discovery_msg(state_topic, address):
    discovery_topic = "homeassistant/sensor/xiaomi_lywsd03mmc_" + address + "/battery/config"
    payload = {
        'name': 'xiaomi lywsd03mmc ' + address + ' battery',
        'unique_id': 'xiaomi_lywsd03mmc_' + address + '_battery',
        'state_topic': state_topic,
        'unit_of_measurement': '%',
        'device_class': 'battery',
        'value_template': '{{ value_json.battery }}',
        'force_update': True,
        'expire_after': 120
    }
    client.publish(discovery_topic, json.dumps(payload).encode())


def send_mqtt_sensor_state_msg(state_topic, values):
    payload = {
        'temperature': str(values.temperature),
        'humidity': str(values.humidity),
        'battery': str(values.battery_level)
    }
    client.publish(state_topic, json.dumps(payload).encode())


def send(values):
    address = ''.join('{:02x}'.format(x) for x in values.address)
    state_topic = "xiaomi/lywsd03mmc/" + address + "/state"

    send_mqtt_temperature_discovery_msg(state_topic, address)
    send_mqtt_humidity_discovery_msg(state_topic, address)
    send_mqtt_battery_discovery_msg(state_topic, address)

    send_mqtt_sensor_state_msg(state_topic, values)
