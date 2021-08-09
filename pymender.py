#!/usr/bin/env python3

# Copyright (c) 2021 Iain Menzies-Runciman
# 
# Licensed under the MIT License:
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from typing import Optional
import requests
import json
import os.path

class Mender:
    def __init__(self, host_url: Optional[str] = "https://hosted.mender.io") -> None:
        self.host_url = host_url
        self.authentication = None
        self.token = None
        self.errors = None
        self.status_code = None

    def sendCmd(self, url: str, headers: dict) -> dict:
        pass

    def makeHeader(self, headers: dict = {}) -> dict:
        base_header = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        # If we are authenticated with a JWT, include it
        if self.authentication == "jwt" and self.token is not None:
            base_header['Authorization'] = "Bearer {}".format(self.token)
        for key, value in headers.items():
            base_header[key] = value

        return base_header

    def login(self, username: str, password: str) -> bool:
        logged_in = False
        self.errors = None
        headers = self.makeHeader({'Accept': 'application/jwt'})

        url = "{}/api/management/v1/useradm/auth/login".format(self.host_url)
        result = requests.post(url, 
            auth=(username, password), 
            headers = headers)

        self.status_code = result.status_code
        if result.status_code == 200:
            self.token = result.text
            self.authentication = "jwt"
            logged_in = True
        else:
            self.errors = result.text
        
        return logged_in

    def logout(self) -> bool:
        if self.authentication is not None:
            headers = self.makeHeader()
            url = "{}/api/management/v1/useradm/auth/logout".format(self.host_url)
            result = requests.post(url, headers = headers)
            if result.status_code == 202:
                self.token = None
                self.authentication = None
            else:
                print(result.status_code)
                print(result.text)
            
            if self.authentication == None:
                return True
            else:
                return False

    def auth(self):
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-MEN-Signature': 'string',
            'Authorization': "Bearer {}".format(self.token)
        }
        url = "{}/api/management/v1/useradm/auth/auth_requests".format(self.host_url)
        result = requests.post(url, headers = headers)
        print(result.json())

    def listUsers(self) -> list:
        users = []
        if self.authentication is not None:
            headers = self.makeHeader()
            url = "{}/api/management/v1/useradm/users".format(self.host_url)
            result = requests.get(url, headers = headers)
            if result.status_code == 200:
                users = result.json()
            else:
                print(result.status_code)
                print(result.text)
        return users

    def listDevices(self, 
        page: Optional[int]=None, 
        per_page: Optional[int]=None, 
        sort: Optional[str]=None,
        has_group: Optional[bool]=False,
        group: Optional[str]=None) -> list:

        devices = []
        if self.authentication is not None:

            body = {}
            if page is not None:
                body['page'] = page
            if per_page is not None:
                body['per_page'] = per_page
            if sort is not None:
                body['sort'] = sort
            if has_group:
                body['has_group'] = has_group
            if group is not None:
                body['group'] = group

            headers = self.makeHeader()
            url = "{}/api/management/v1/inventory/devices".format(self.host_url)
            result = requests.get(url, headers = headers, params=body)
            if result.status_code == 200:
                devices = result.json()
            else:
                print(result.status_code)
                print(result.text)
        return devices

    def removeDevice(self, device_id: str) -> bool:
        if self.authentication is not None:
            headers = self.makeHeader()
            url = "{}/api/management/v2/devauth/devices/{}".format(self.host_url, device_id)
            result = requests.delete(url, headers = headers)
            if result.status_code == 204:
                # it worked
                return True
            else:
                print(result.status_code)
                print(result.text)

        return False

    def listReleases(self) -> list:
        releases = []
        if self.authentication is not None:
            headers = self.makeHeader()
            url = "{}/api/management/v1/deployments/deployments/releases".format(self.host_url)
            result = requests.get(url, headers = headers)
            if result.status_code == 200:
                releases = result.json()
            else:
                print(result.status_code)
                print(result.text)
        return releases

    def newDeployment(self, name: str, 
        artifact_name: str, 
        devices=[], 
        all_devices: Optional[bool]=False, 
        phases=None, 
        retries: Optional[int]=1) -> str:
        if self.authentication is not None:
            headers = self.makeHeader()
            url = "{}/api/management/v1/deployments/deployments".format(self.host_url)
            body = {
                "name": name,
                "artifact_name": artifact_name,
                "retries": retries
            }
            if all_devices:
                body["all_devices"] = True
            elif len(devices) > 0:
                body["devices"] = devices

            if phases is not None:
                body["phases"] = phases

            result = requests.post(url, data=json.dumps(body), headers=headers)

            if result.status_code == 201:
                # it worked
                location = os.path.basename(result.headers['Location'])
                return location
            else:
                print(result.status_code)
                print(result.text)

        return ""

    def deploymentStatus(self, deployment_id: str):
        if self.authentication is not None:
            headers = self.makeHeader()
            url = "{}/api/management/v1/deployments/deployments/{}".format(self.host_url, deployment_id)
            body = {}

            status = None
            result = requests.get(url, headers=headers)

            if result.status_code == 200:
                status = result.json()
            else:
                print(result.status_code)
                print(result.text)

        return status

    def getArtifactLink(self, artifact_id: str) -> str:
        if self.authentication is not None:
            headers = self.makeHeader()
            url = "{}/api/management/v1/deployments/artifacts/{}/download".format(self.host_url, artifact_id)
            body = {}

            link = None
            result = requests.get(url, headers=headers)        
            if result.status_code == 200:
                link = result.json()
            else:
                print(result.status_code)
                print(result.text)

        return link

