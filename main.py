import asyncio

import domoticz

from bleak import BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

import node_red
from XiaomiLYWSD03MMC import XiaomiLYWSD03MMC
from XiaomiLYWSD03MMC import XIAOMI_LYWSD03MMC_PROFILE_CUSTOM
from device_list import devices


keeping_track = {}


def simple_callback(device: BLEDevice, advertisement_data: AdvertisementData):
    if XIAOMI_LYWSD03MMC_PROFILE_CUSTOM in advertisement_data.service_data:
        service_data = advertisement_data.service_data[XIAOMI_LYWSD03MMC_PROFILE_CUSTOM]
        values = XiaomiLYWSD03MMC()
        values.address = ':'.join('{:02x}'.format(x) for x in service_data[0:6])
        values.temperature = float(int.from_bytes(service_data[6:8], byteorder='big'))/10
        values.humidity = service_data[8]
        values.battery_level = service_data[9]
        values.battery_voltage = int.from_bytes(service_data[10:12], byteorder='big')
        values.frame = service_data[12]

        if values.address not in devices:
            return

        send = False
        track = keeping_track.get(values.address)
        if track:
            if values.frame != track.frame:
                send = True
        else:
            send = True

        if send:
            keeping_track[values.address] = values
            print(device.address,
                  devices[values.address]["name"],
                  "keeping_track: %d" % len(keeping_track)
                  )
            node_red.send(device, values)
            # domoticz.send(device, values)


async def run():
    scanner = BleakScanner()
    scanner.register_detection_callback(simple_callback)

    while True:
        await scanner.start()
        await asyncio.sleep(5.0)
        await scanner.stop()


loop = asyncio.get_event_loop()
loop.run_until_complete(run())