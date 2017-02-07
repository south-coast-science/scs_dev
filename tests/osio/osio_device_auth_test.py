#!/usr/bin/env python3

"""
Created on 17 Nov 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

username, device_id, device_password

examples:
{"msg": null, "err": {"code": "UNKNOWN_CMD", "value": "hello"}}
{"msg": {"op": "scs-rpi-006", "spec": "scs-rpi-006"}, "err": null}
"""

from scs_core.osio.client.device_auth import DeviceAuth

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

username = "southcoastscience-dev"
print(username)

device_id = "5406"
print(device_id)

device_password = "jtxSrK2e"
print(device_password)

print("-")


# --------------------------------------------------------------------------------------------------------------------

auth = DeviceAuth(username, device_id, device_password)
print(auth)
print("-")

auth.save(Host)

auth = DeviceAuth.load_from_host(Host)
print(auth)
print("-")
