#!/usr/bin/env python3

'''
Created on 11 Nov 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
'''

import sys

from scs_core.osio.client.device_auth import DeviceAuth
from scs_core.osio.client.topic_client import TopicClient

from scs_host.client.mqtt_client import MQTTClient


# --------------------------------------------------------------------------------------------------------------------

device_id = "5404"                      # listener
device_password = "mh7nxziu"

username = "southcoastscience-dev"

topic = "/users/southcoastscience-dev/test/json"

auth = DeviceAuth(username, device_id, device_password)
print(auth)


# --------------------------------------------------------------------------------------------------------------------

message_client = MQTTClient()

topic_client = TopicClient(message_client, auth)
print(topic_client)
print("-")

try:
    for path_dict in topic_client.subscribe(topic):
        print(path_dict)
        print(path_dict.node('rec', 'val.mcu.tmp'))
        print("-")
        sys.stdout.flush()

except KeyboardInterrupt:
    print()
    pass
