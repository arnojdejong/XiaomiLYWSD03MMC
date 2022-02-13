import logging
import requests

logger = logging.getLogger(__name__)


class Domoticz:
    def __init__(self):
        self.url = None
        self.devices = None

    def init(self, config, devices):
        logger.debug('init')
        if not config:
            return
        if not devices:
            return

        self.devices = devices

        do_config = config.get('domoticz')
        if not do_config:
            return

        self.url = do_config.get('url')
        if not self.url:
            return

    def start(self):
        logger.debug('start')

    def send(self, device, values):
        if not self.url:
            return

        address = ':'.join('{:02x}'.format(x) for x in values.address)
        if address not in self.devices:
            logger.debug('{} not in device_list'.format(address))
            return

        hum = values.humidity
        hum_stat = 0
        if hum < 30:
            hum_stat = 2
        elif 30 <= hum < 45:
            hum_stat = 0
        elif 45 <= hum < 70:
            hum_stat = 1
        elif hum >= 70:
            hum_stat = 3

        payload = {
            "type": "command",
            "param": "udevice",
            "idx": self.devices[address]["idx"],
            "nvalue": 0,
            "svalue": str(values.temperature) + ";" + str(values.humidity) + ";" + str(hum_stat)
        }

        try:
            response = requests.get(self.url, params=payload)
            logger.debug(response.url)

            # If the response was successful, no Exception will be raised
            response.raise_for_status()
        except Exception as err:
            logger.exception('error occurred')
