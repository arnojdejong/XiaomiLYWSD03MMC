# Xiaomi LYWSD03MMC
Simple python program to publish custom Xiaomi LYWSD03MMC advertisments(https://github.com/atc1441/ATC_MiThermometer) to a MQTT broker or Domoticz.

Works on Raspberry Pi

## start application
virtualenv -p python3 venv
source venv/bin/activate
pip install -r requirements.txt
deactivate

sudo ./run

### device_list.py
contains all devices to publish
- key: device.address in lower case seperated by :
- name: simple description used as informative field in mqtt payload
- idx: idx for Domoticz

### node_red.py
mqtt client for publishing a custom payload I use for Node Red and Grafana
- broker_address: mqtt broker address
- topic: topic where the advertisement is posted

### domoticz.py
domoticz client
- url: url to post the payload
