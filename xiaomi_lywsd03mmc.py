import asyncio
import json
import logging
from logging.handlers import RotatingFileHandler

from bleak import BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

from XiaomiLYWSD03MMC import XiaomiLYWSD03MMC
from XiaomiLYWSD03MMC import XIAOMI_LYWSD03MMC_PROFILE_CUSTOM
from domoticz import Domoticz
from home_assistant import HomeAssistant
from node_red import NodeRed

keeping_track = {}
home_assistant = HomeAssistant()
node_red = NodeRed()
domoticz = Domoticz()


def simple_callback(device: BLEDevice, advertisement_data: AdvertisementData):
    if XIAOMI_LYWSD03MMC_PROFILE_CUSTOM in advertisement_data.service_data:
        service_data = advertisement_data.service_data[XIAOMI_LYWSD03MMC_PROFILE_CUSTOM]
        values = XiaomiLYWSD03MMC()
        values.address = service_data[0:6]
        values.address_str = ':'.join('{:02x}'.format(x) for x in service_data[0:6])
        values.temperature = float(int.from_bytes(service_data[6:8], byteorder='big', signed=True))/10
        values.humidity = service_data[8]
        values.battery_level = service_data[9]
        values.battery_voltage = int.from_bytes(service_data[10:12], byteorder='big')
        values.frame = service_data[12]

        send = False
        track = keeping_track.get(values.address_str)
        if track:
            if values.frame != track.frame:
                send = True
        else:
            send = True

        if send:
            keeping_track[values.address_str] = values

            text = '"{}", frame: {}'.format(
                device.address,
                values.frame
            )
            logging.debug(text)

            domoticz.send(device, values)
            home_assistant.send(values)
            node_red.send(device, values)


async def run():
    scanner = BleakScanner()
    scanner.register_detection_callback(simple_callback)

    while True:
        await scanner.start()
        await asyncio.sleep(5.0)
        await scanner.stop()

if __name__ == '__main__':
    rootLogger = logging.getLogger()

    log_path = "logs/logfile"
    logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)

    timedHandler = RotatingFileHandler(log_path, maxBytes=30*1024*1024, backupCount=10)
    timedHandler.setFormatter(logFormatter)
    rootLogger.addHandler(timedHandler)

    logging.getLogger('bleak').propagate = False
    logging.getLogger("bleak").setLevel(logging.CRITICAL)

    rootLogger.setLevel(logging.DEBUG)  # temp to catch output when reading settings file

    logging.debug("read config files")
    config = None
    config_file = 'config/config.json'
    try:
        with open(config_file) as data_file:
            config = json.loads(data_file.read())
            data_file.close()
    except:
        logging.exception('config.json')

    _devices = {}
    devices_file = 'config/devices.json'
    try:
        with open(devices_file) as data_file:
            _devices = json.loads(data_file.read())
            data_file.close()
    except:
        logging.exception('devices.json')

    logging.debug("init connectors")
    node_red.init(config, _devices)
    home_assistant.init(config)
    domoticz.init(config, _devices)

    logging.debug("start connectors")
    node_red.start()
    home_assistant.start()
    domoticz.start()

    logging.debug("loop forever")
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(run())
    except:
        logging.exception('loop forever')

    logging.debug("exit")
