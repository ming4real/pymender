#!/usr/bin/python3

import configparser
import json
import argparse 

import pymender

#mender.newDeployment("master__whuba__production__21.5.0.RC_76838", "master__whuba__production__21.5.0.RC_76838", devices=["09130b12-afc3-46a7-8a5a-0fedce87dbac"])

parser = argparse.ArgumentParser(description='Create a new mender deployment')
parser.add_argument("name")
parser.add_argument("device_id")
args = parser.parse_args()

deploy_name = args.name
device_id = args.device_id

config = configparser.ConfigParser()
config.read('config.ini')

username = config["mender"]["username"]
password = config["mender"]["password"]

mender = pymender.Mender()
mender.login(username, password)

deploy_id = mender.newDeployment("ming_deployment", deploy_name, devices=[device_id])
print(deploy_id)

