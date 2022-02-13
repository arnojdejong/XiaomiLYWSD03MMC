import json
import logging

import paho.mqtt.client as mqtt
from pprint import pprint

logger = logging.getLogger(__name__)


class NodeRed:
    def __init__(self):
        self.client = None
        self.broker_address = None
        self.username = None
        self.password = None
        self.topic = None

        self.devices = None

    def init(self, config, devices):
        if not config:
            return
        if not devices:
            return
        logger.debug('init')
        self.devices = devices

        nr_config = config.get('node_red')
        if not nr_config:
            return

        logging.debug("nr: creating new instance")
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
        if not self.broker_address:
            return
        logger.debug('start')

        try:
            logging.debug("nr: connecting to broker")
            self.client.connect(self.broker_address)  # connect to broker
            logging.debug("nr: connected to broker")
            self.client.loop_start()
        except:
            logging.exception('error occurred')

    def send(self, device, values):
        if not self.topic:
            return

        address = ':'.join('{:02x}'.format(x) for x in values.address)

        payload = {
            "type": "Xiaomi LYWSD03MMC",
            "location": self.devices[address]["name"],
            "address": address,
            "temperature_celcius": values.temperature,
            "humidity": values.humidity,
            "battery_level": values.battery_level,
            "battery_voltage": values.battery_voltage,
            "frame_count": values.frame,
            "rssi": device.rssi
        }
        self._publish(self.topic, json.dumps(payload).encode())

    def _publish(self, topic, data):
        try:
            logger.debug('publish: {}'.format(topic))
            self.client.publish(topic, data)
        except Exception as err:
            logger.exception('error occurred')

