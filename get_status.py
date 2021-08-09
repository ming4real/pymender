#!/usr/bin/python3

import configparser
import json
import argparse 
import time

import pymender

parser = argparse.ArgumentParser(description='Get the status of a Mender deployment')
parser.add_argument("deploy_id")
args = parser.parse_args()

deploy_id = args.deploy_id

config = configparser.ConfigParser()
config.read('config.ini')

username = config["mender"]["username"]
password = config["mender"]["password"]

mender = pymender.Mender()
mender.login(username, password)

deploy_status = "unknown"
while deploy_status != "finished":
    status = mender.deploymentStatus(deploy_id)
    deploy_status = status['status']
    print(deploy_status)
    time.sleep(60)

print(deploy_status)
