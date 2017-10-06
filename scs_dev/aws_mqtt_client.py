#!/usr/bin/env python3

"""
Created on 4 Oct 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

WARNING: only one MQTT client should run at any one time, per a TCP/IP host.

Requires Endpoint and ClientCredentials documents.

command line example:
./aws_mqtt_client.py
"""

import json
# import logging
import sys
# import time

from collections import OrderedDict

from scs_core.aws.client.mqtt_client import MQTTClient
from scs_core.aws.client.client_credentials import ClientCredentials
from scs_core.aws.service.endpoint import Endpoint

from scs_core.data.json import JSONify
# from scs_core.data.localized_datetime import LocalizedDatetime
from scs_core.data.publication import Publication

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

    topic = "bruno/1"

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # endpoint...
        endpoint = Endpoint.load(Host)

        if endpoint is None:
            print("Endpoint not available.", file=sys.stderr)
            exit(1)

        # endpoint...
        credentials = ClientCredentials.load(Host)

        if credentials is None:
            print("ClientID not available.", file=sys.stderr)
            exit(1)

        # logger...
        # logger = logging.getLogger("AWSIoTPythonSDK.core")
        # logger.setLevel(logging.DEBUG)
        #
        # streamHandler = logging.StreamHandler()
        # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        # streamHandler.setFormatter(formatter)
        #
        # logger.addHandler(streamHandler)

        # client...
        client = MQTTClient(endpoint, credentials)

        print(client, file=sys.stderr)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        handler = AWSMQTTHandler()

        client.connect()
        # client.subscribe(topic, 1, handler.handle)
        # time.sleep(2)

        for line in sys.stdin:
            try:
                jdict = json.loads(line, object_pairs_hook=OrderedDict)
            except ValueError:
                continue

            publication = Publication.construct_from_jdict(jdict)

            client.publish(publication)


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
