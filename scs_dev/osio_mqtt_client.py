#!/usr/bin/env python3

"""
Created on 23 Mar 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

WARNING: only one MQTT client can run at any one time on a TCP/IP host.

Requires APIAuth and ClientAuth documents.

command line example:
osio_mqtt_client.py -v /orgs/south-coast-science-dev/development/loc/3/gases \
/orgs/south-coast-science-dev/development/loc/3/particulates
"""

import json
import random
import sys
import time

from collections import OrderedDict

from scs_analysis.cmd.cmd_osio_mqtt_client import CmdOSIOMQTTClient

from scs_core.data.json import JSONify
from scs_core.data.localized_datetime import LocalizedDatetime
from scs_core.data.publication import Publication

from scs_core.osio.client.api_auth import APIAuth
from scs_core.osio.client.client_auth import ClientAuth
from scs_core.osio.manager.topic_manager import TopicManager

from scs_core.sys.exception_report import ExceptionReport

from scs_host.client.http_client import HTTPClient
from scs_host.client.mqtt_client import MQTTClient
from scs_host.client.mqtt_client import MQTTSubscriber

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------
# subscription handler...

class OSIOMQTTResponder(object):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, verbose):
        """
        Constructor
        """
        self.__verbose = verbose


    # ----------------------------------------------------------------------------------------------------------------

    def print_publication(self, pub):
        print(JSONify.dumps(pub))
        sys.stdout.flush()

        if not self.__verbose:
            return

        print("received: %s" % JSONify.dumps(pub), file=sys.stderr)
        sys.stderr.flush()


    def print_status(self, status):
        if not self.__verbose:
            return

        now = LocalizedDatetime.now()
        print("%s:         mqtt: %s" % (now.as_iso8601(), status), file=sys.stderr)
        sys.stderr.flush()


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "OSIOMQTTResponder:{verbose:%s}" % self.__verbose


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    client = None

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdOSIOMQTTClient()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit()

    if cmd.verbose:
        print(cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # APIAuth...
        api_auth = APIAuth.load_from_host(Host)

        if api_auth is None:
            print("APIAuth not available.", file=sys.stderr)
            exit()

        if cmd.verbose:
            print(api_auth, file=sys.stderr)

        # ClientAuth...
        client_auth = ClientAuth.load_from_host(Host)

        if client_auth is None:
            print("ClientAuth not available.", file=sys.stderr)
            exit()

        if cmd.verbose:
            print(client_auth, file=sys.stderr)

        # manager...
        manager = TopicManager(HTTPClient(), api_auth.api_key)

        if cmd.verbose:
            print(manager, file=sys.stderr)

        # responder...
        responder = OSIOMQTTResponder(cmd.verbose)

        if cmd.verbose:
            print(responder, file=sys.stderr)

        # client...
        subscribers = [MQTTSubscriber(topic, responder.print_publication) for topic in cmd.topics]

        client = MQTTClient(*subscribers)
        client.connect(ClientAuth.MQTT_HOST, client_auth.client_id, client_auth.user_id, client_auth.client_password)

        if cmd.verbose:
            print(client, file=sys.stderr)
            sys.stderr.flush()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        # check topics...
        unavailable = False
        for topic in cmd.topics:
            if not manager.find(topic):
                print("Topic not available: %s" % topic, file=sys.stderr)
                unavailable = True

        if unavailable:
            exit()

        # publish loop...
        if cmd.publish:
            for line in sys.stdin:
                try:
                    datum = json.loads(line, object_pairs_hook=OrderedDict)
                except ValueError:
                    responder.print_status("bad datum: %s" % line.strip())
                    continue

                while True:
                    publication = Publication.construct_from_jdict(datum)

                    try:
                        if 'rec' in publication.payload:
                            responder.print_status(publication.payload['rec'])

                        success = client.publish(publication, ClientAuth.MQTT_TIMEOUT)

                        if not success:
                            responder.print_status("abandoned")

                        break

                    except Exception as ex:
                        if cmd.verbose:
                            print(JSONify.dumps(ExceptionReport.construct(ex)))
                            sys.stderr.flush()

                    time.sleep(random.uniform(1.0, 2.0))           # Don't hammer the client!

                responder.print_status("done")

                if cmd.echo:
                    print(line, end="")
                    sys.stdout.flush()

        # subscribe loop...
        if cmd.topics:
            while True:
                time.sleep(0.1)


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt as ex:
        if cmd.verbose:
            print("osio_mqtt_client: KeyboardInterrupt", file=sys.stderr)

    except Exception as ex:
        print(JSONify.dumps(ExceptionReport.construct(ex)), file=sys.stderr)

    finally:
        if client:
            client.disconnect()
