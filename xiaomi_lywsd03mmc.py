import asyncio
import json

from bleak import BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

from XiaomiLYWSD03MMC import XiaomiLYWSD03MMC
from XiaomiLYWSD03MMC import XIAOMI_LYWSD03MMC_PROFILE_CUSTOM
from device_list import devices
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

            text = '"{}", "{}",  frame: {}'.format(
                device.address,
                devices.get(values.address_str, {}).get('name', ''),
                values.frame
            )
            print(text)

            node_red.send(device, values)
            domoticz.send(device, values)
            home_assistant.send(values)


async def run():
    scanner = BleakScanner()
    scanner.register_detection_callback(simple_callback)

    while True:
        await scanner.start()
        await asyncio.sleep(5.0)
        await scanner.stop()

if __name__ == '__main__':
    config = None
    config_file = 'config/config.json'
    with open(config_file) as data_file:
        config = json.loads(data_file.read())
        data_file.close()

    _devices = {}
    devices_file = 'config/devices.json'
    with open(devices_file) as data_file:
        _devices = json.loads(data_file.read())
        data_file.close()

    devices = _devices

    node_red.init(config)
    home_assistant.init(config)
    domoticz.init(config)

    node_red.start()
    home_assistant.start()
    domoticz.start()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
