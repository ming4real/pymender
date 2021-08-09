#!/usr/bin/python3

import pymender
import json
import datetime
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

username = config["mender"]["username"]
password = config["mender"]["password"]

mender = pymender.Mender()
mender.login(username, password)

devices = mender.listDevices(per_page=500, page=1)

dev_dict = {}
dupes = {}
for dev in devices:
    device_id = dev['id']
    raw_mac = ""
    mac = ""
    for attr in dev['attributes']:
        if attr['name'] == "mac":
            raw_mac = attr['value']
            mac = raw_mac.lower()

        if attr['name'] == "updated_ts":
            updated_ts = attr['value'].split(".")[0]
    
    if not dev_dict.get(mac):
        dev_dict[mac] = [device_id, updated_ts, raw_mac]
    else:
        previous_dev_id = dev_dict[mac][0]
        previous_ts = dev_dict[mac][1]
        previous_mac = dev_dict[mac][2]

        # Find the older one...
        this_dt = datetime.datetime.fromisoformat(updated_ts)
        old_dt = datetime.datetime.fromisoformat(previous_ts)

        if old_dt > this_dt:
            print("Older: ", old_dt, this_dt)
        else:
            print("Newer: ", this_dt, old_dt)
            if mender.removeDevice(previous_dev_id):
                print("{} - {} removed".format(previous_mac, previous_dev_id))
            else:
                print("Failed to remove {}".format(previous_dev_id))

        dupes[mac] = {device_id : updated_ts, previous_dev_id : previous_ts, "mac": raw_mac, "previous": previous_mac}

print(json.dumps(dupes))