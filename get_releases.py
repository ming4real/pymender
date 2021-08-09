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

releases = mender.listReleases()

db_connection = mysql.connector.connect(
    host=db_host,
    user=db_user, 
    password=db_password,
    database=db_database)
cursor = db_connection.cursor()

sql = """TRUNCATE releases"""
cursor.execute(sql)

sql = """TRUNCATE artifacts"""
cursor.execute(sql)

for release in releases:
    release_name = release["Name"]
    sql = """INSERT INTO releases (name) VALUES ("{}")""".format(release_name)
    cursor.execute(sql)
    release_id = cursor.lastrowid

    for artifact in release["Artifacts"]:
        mender_id = artifact["id"]
        artifact_name = artifact["name"]
        file_checksum = artifact["updates"][0]["files"][0]["checksum"]
        file_size = artifact["updates"][0]["files"][0]["size"]
        file_type =  artifact["updates"][0]["type_info"]["type"]
        provides_name = artifact["artifact_provides"]["artifact_name"]
        try:
            provides_checksum = artifact["artifact_provides"]["rootfs-image.checksum"]
        except KeyError:
            provides_checksum = artifact["artifact_provides"]["rootfs_image_checksum"]
            
        depends_checksum = None
        try:
            depends_checksum = artifact["artifact_depends"]["rootfs-image.checksum"]
        except KeyError:
            try:
                depends_checksum = artifact["artifact_depends"]["rootfs_image_checksum"]
            except KeyError:
                pass

        artifact_size = artifact["size"]

        artifact_sql = """ 
INSERT INTO artifacts 
(release_id, mender_id, artifact_name, file_checksum, file_size, file_type, provides_name, provides_checksum, depends_checksum, artifact_size) 
VALUES ({}, "{}", "{}", "{}", {}, "{}", "{}", "{}", "{}", {})
""".format(release_id, mender_id, artifact_name, file_checksum, file_size, file_type, provides_name, provides_checksum, depends_checksum, artifact_size)
        print(artifact_sql)
        cursor.execute(artifact_sql)

    # db_connection.commit()


db_connection.commit()


