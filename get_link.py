#!/usr/bin/python3

import configparser
import json
import argparse 

import pymender

parser = argparse.ArgumentParser(description='Get the download URL of a Mender artifact')
parser.add_argument("artifact_id")
args = parser.parse_args()

artifact_id = args.artifact_id

config = configparser.ConfigParser()
config.read('config.ini')

username = config["mender"]["username"]
password = config["mender"]["password"]

mender = pymender.Mender()
mender.login(username, password)

link = mender.getArtifactLink(artifact_id)

print(link)
