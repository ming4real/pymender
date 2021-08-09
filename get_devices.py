#!/usr/bin/python3

import configparser
import json
import mysql.connector

import pymender

config = configparser.ConfigParser()
config.read('config.ini')

username = config["mender"]["username"]
password = config["mender"]["password"]

db_host = config["database"]["host"]
db_user = config["database"]["user"]
db_password = config["database"]["password"]
db_database = config["database"]["database"]


mender = pymender.Mender()
mender.login(username, password)

db_connection = mysql.connector.connect(
    host=db_host,
    user=db_user, 
    password=db_password,
    database=db_database)
cursor = db_connection.cursor()

sql = """TRUNCATE devices"""
cursor.execute(sql)

new_devices = []

page = 1
devices = mender.listDevices(page=page, per_page=200)

while len(devices) > 0:
    for device in devices:
        device_id = device["id"]

        mac_address = ""
        artifact_name = "" 

        for attribute in device["attributes"]:
            name = attribute["name"]
            value = attribute["value"]
            scope = attribute["scope"]

            if name == "mac":
                mac_address = value
            elif name == "artifact_name":
                artifact_name = value
            
        new_devices.append((device_id, mac_address, artifact_name))

    page += 1
    print(page)
    devices = mender.listDevices(page=page, per_page=200)

print(len(new_devices))
if len(new_devices) > 0:
    sql = """INSERT INTO devices (device_id, mac_address, artifact_name) VALUES (%s, %s, %s)"""
    cursor.executemany(sql, new_devices)
    db_connection.commit()

