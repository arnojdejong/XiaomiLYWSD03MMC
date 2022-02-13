import json
import paho.mqtt.client as mqtt


class HomeAssistant:
    def __init__(self):
        self.client = None
        self.broker_address = None
        self.username = None
        self.password = None

    def init(self, config):
        ha_config = config.get('home_assistant')
        if not ha_config:
            return

        print("ha: creating new instance")
        self.client = mqtt.Client()

        self.broker_address = ha_config.get('broker_address')
        if not self.broker_address:
            return

        self.username = ha_config.get('broker_username')
        self.password = ha_config.get('broker_password')
        if self.username:
            self.client.username_pw_set(self.username, self.password)

    def start(self):
        print("ha: start")
        if not self.broker_address:
            return

        print("ha: connecting to broker")
        self.client.connect(self.broker_address)  # connect to broker
        print("ha: connected to broker")
        self.client.loop_start()

    def send_mqtt_temperature_discovery_msg(self, state_topic, address):
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
        self.client.publish(discovery_topic, json.dumps(payload).encode())

    def send_mqtt_humidity_discovery_msg(self, state_topic, address):
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
        self.client.publish(discovery_topic, json.dumps(payload).encode())

    def send_mqtt_battery_discovery_msg(self, state_topic, address):
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
        self.client.publish(discovery_topic, json.dumps(payload).encode())

    def send_mqtt_sensor_state_msg(self, state_topic, values):
        payload = {
            'temperature': str(values.temperature),
            'humidity': str(values.humidity),
            'battery': str(values.battery_level)
        }
        self.client.publish(state_topic, json.dumps(payload).encode())

    def send(self, values):
        address = ''.join('{:02x}'.format(x) for x in values.address)
        state_topic = "xiaomi/lywsd03mmc/" + address + "/state"

        self.send_mqtt_temperature_discovery_msg(state_topic, address)
        self.send_mqtt_humidity_discovery_msg(state_topic, address)
        self.send_mqtt_battery_discovery_msg(state_topic, address)

        self.send_mqtt_sensor_state_msg(state_topic, values)
