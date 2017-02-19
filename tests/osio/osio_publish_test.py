#!/usr/bin/env python3

"""
Created on 11 Nov 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import sys

from scs_core.data.json import JSONify
from scs_core.data.localized_datetime import LocalizedDatetime
from scs_core.osio.client.client_auth import ClientAuth
from scs_core.osio.client.topic_client import TopicClient
from scs_core.sample.sample_datum import SampleDatum
from scs_core.sync.sampler import Sampler

from scs_host.client.mqtt_client import MQTTClient

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

device_id = "5406"                  # json-test
device_password = "jtxSrK2e"

user_id = "southcoastscience-dev"

topic = "/users/southcoastscience-dev/test/json"

auth = ClientAuth(user_id, device_id, device_password)
print(auth)


# --------------------------------------------------------------------------------------------------------------------

class MCUTempSampler(Sampler):
    """
    classdocs
    """
    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, interval, sample_count = 0):
        """
        Constructor
        """
        Sampler.__init__(self, interval, sample_count)


    # ----------------------------------------------------------------------------------------------------------------

    def sample(self):
        return 'mcu', Host.mcu_temp()


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "MCUTempSampler:{timer:%s, sample_count:%d}" % (self.timer, self.sample_count)


# --------------------------------------------------------------------------------------------------------------------

message_client = MQTTClient()

topic_client = TopicClient(message_client, auth)
print(topic_client)
print("-")

temp = MCUTempSampler(5, 0)

try:
    for sample in temp.samples():
        recorded = LocalizedDatetime.now()
        datum = SampleDatum(recorded, sample)

        topic_client.publish(topic, datum)

        print(JSONify.dumps(datum))
        sys.stdout.flush()

except KeyboardInterrupt:
    print()
    pass


