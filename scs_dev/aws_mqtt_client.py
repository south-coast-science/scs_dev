#!/usr/bin/env python3

"""
Created on 4 Oct 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

WARNING: only one MQTT client should run at any one time, per a TCP/IP host.

Requires APIAuth and ClientAuth documents.

command line example:
./osio_mqtt_client.py \
/orgs/south-coast-science-dev/unep/loc/1/gases gases.uds \
/orgs/south-coast-science-dev/unep/loc/1/particulates particulates.uds \
-p osio_mqtt_pub.uds -s -e
"""

import json
import logging
import sys
import time

from collections import OrderedDict

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

from scs_core.aws.client.client_id import ClientID
from scs_core.aws.service.endpoint import Endpoint

from scs_core.data.json import JSONify
from scs_core.data.localized_datetime import LocalizedDatetime

from scs_core.sys.exception_report import ExceptionReport

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------
# subscription handler...

class AWSMQTTHandler(object):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, comms=None, echo=False, verbose=False):
        """
        Constructor
        """
        self.__comms = comms

        self.__echo = echo
        self.__verbose = verbose


    # ----------------------------------------------------------------------------------------------------------------

    def handle(self, client, userdata, message):
        print("Received a new message: ")
        print(message.payload)
        print("from topic: ")
        print(message.topic)
        print("--------------\n\n")

        # if self.__echo:
        #     print(JSONify.dumps(pub))
        #     sys.stdout.flush()
        #
        # if self.__verbose:
        #     print("received: %s" % JSONify.dumps(pub), file=sys.stderr)
        #     sys.stderr.flush()


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "AWSMQTTHandler:{comms:%s, echo:%s, verbose:%s}" % \
               (self.__comms, self.__echo, self.__verbose)


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    client = None
    pub_comms = None


    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cert_dir = Host.aws_dir() + 'cert/'

    topic = "bruno/1"

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        endpoint = Endpoint.load(Host)

        if endpoint is None:
            print("Endpoint not available.", file=sys.stderr)
            exit(1)

        client_id = ClientID.load(Host)

        if client_id is None:
            print("ClientID not available.", file=sys.stderr)
            exit(1)

        logger = logging.getLogger("AWSIoTPythonSDK.core")
        logger.setLevel(logging.DEBUG)

        streamHandler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        streamHandler.setFormatter(formatter)

        logger.addHandler(streamHandler)

        client = AWSIoTMQTTClient(client_id.name)

        client.configureEndpoint(endpoint.endpoint_host, 8883)
        client.configureCredentials(client_id.root_ca_file_path, client_id.private_key_path, client_id.certificate_path)

        client.configureAutoReconnectBackoffTime(1, 32, 20)
        client.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
        client.configureDrainingFrequency(2)  # Draining: 2 Hz
        client.configureConnectDisconnectTimeout(30)  # 10 sec
        client.configureMQTTOperationTimeout(30)  # 5 sec


        # ------------------------------------------------------------------------------------------------------------
        # run...

        handler = AWSMQTTHandler()

        client.connect()
        client.subscribe(topic, 1, handler.handle)
        time.sleep(2)

        for line in sys.stdin:
            datum = line.strip()

            if datum is None:
                break

            client.publish(topic, datum, 1)


        # ----------------------------------------------------------------------------------------------------------------
        # end...

    except KeyboardInterrupt:
        # if cmd.verbose:
        #     print("osio_mqtt_client: KeyboardInterrupt", file=sys.stderr)
        pass

    except Exception as ex:
        print(JSONify.dumps(ExceptionReport.construct(ex)), file=sys.stderr)

    finally:
        if client:
            client.disconnect()
