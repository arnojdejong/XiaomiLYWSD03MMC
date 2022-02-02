from pprint import pprint

import requests
from requests import HTTPError

from device_list import devices

url = "http://127.0.0.1:8080/json.htm"


def send(device, values):
    address = ':'.join('{:02x}'.format(x) for x in values.address)
    if address not in devices:
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
        "idx": devices[address]["idx"],
        "nvalue": 0,
        "svalue": str(values.temperature) + ";" + str(values.humidity) + ";" + str(hum_stat)
    }

    try:
        response = requests.get(url, params=payload)
        print(response.url)

        # If the response was successful, no Exception will be raised
        response.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')  # Python 3.6
    except Exception as err:
        print(f'Other error occurred: {err}')  # Python 3.6
    else:
        print('Success!')
