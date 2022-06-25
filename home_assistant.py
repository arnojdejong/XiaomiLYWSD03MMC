import json
import logging

import paho.mqtt.client as mqtt

logger = logging.getLogger(__name__)


class HomeAssistant:
    def __init__(self):
        self.client = None
        self.broker_address = None
        self.username = None
        self.password = None

        self.initialized = []

    def init(self, config):
        logger.debug('init')

        if not config:
            return

        ha_config = config.get('home_assistant')
        if not ha_config:
            return

        logging.debug("ha: creating new instance")
        self.client = mqtt.Client()

        self.broker_address = ha_config.get('broker_address')
        if not self.broker_address:
            return

        self.username = ha_config.get('broker_username')
        self.password = ha_config.get('broker_password')
        if self.username:
            self.client.username_pw_set(self.username, self.password)

    def start(self):
        logger.debug('start')

        if not self.broker_address:
            return

        try:
            logging.debug("ha: connecting to broker")
            # self.client.on_log = self.on_log
            self.client.on_connect = self.on_connect
            self.client.on_disconnect = self.on_disconnect
            self.client.on_message = self.on_message

            self.client.connect(self.broker_address)  # connect to broker
        except Exception as err:
            logging.exception('error occurred')

        self.client.loop_start()

    def on_log(self, client, userdata, level, buf):
        logging.debug(buf)

    def on_connect(self, client, userdata, flags, rc):
        logging.debug("Connected with result code: "+str(rc))
        self.client.subscribe("homeassistant/status")

        self.initialized = []

    def on_disconnect(self, client, userdata, rc):
        logging.debug("Disconnected with result code: "+str(rc))
        if rc != 0:
            logging.error("Unexpected disconnection: "+str(rc))

    def on_message(self, client, userdata, message):
        logging.debug("message received ", str(message.payload.decode("utf-8")))
        logging.debug("message topic=", message.topic)
        logging.debug("message qos=", message.qos)
        logging.debug("message retain flag=", message.retain)

        if message.topic == 'homeassistant/status':
            if message.payload == 'online':
                logging.debug("homeassistant online")
                self.initialized.clear()

            if message.payload == 'offline':
                logging.debug("homeassistant online")

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
        self._publish(discovery_topic, json.dumps(payload).encode())

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
        self._publish(discovery_topic, json.dumps(payload).encode())

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
        self._publish(discovery_topic, json.dumps(payload).encode())

    def send_mqtt_sensor_state_msg(self, state_topic, values):
        payload = {
            'temperature': str(values.temperature),
            'humidity': str(values.humidity),
            'battery': str(values.battery_level)
        }
        self._publish(state_topic, json.dumps(payload).encode())

    def send(self, values):
        address = ''.join('{:02x}'.format(x) for x in values.address)
        state_topic = "xiaomi/lywsd03mmc/" + address + "/state"

        if address not in self.initialized:
            self.send_mqtt_temperature_discovery_msg(state_topic, address)
            self.send_mqtt_humidity_discovery_msg(state_topic, address)
            self.send_mqtt_battery_discovery_msg(state_topic, address)
            self.initialized.append(address)

        self.send_mqtt_sensor_state_msg(state_topic, values)

    def _publish(self, topic, data):
        try:
            logger.debug('publish: {}'.format(topic))
            info = self.client.publish(topic, data)
            # logger.debug(info)
        except Exception as err:
            logger.exception('error occurred')
