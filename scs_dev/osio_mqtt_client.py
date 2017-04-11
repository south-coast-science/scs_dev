#!/usr/bin/env python3

"""
Created on 23 Mar 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

WARNING: only one MQTT client can run at any one time on a TCP/IP host.

Requires ClientAuth document.

command line example:
./scs_dev/status_sampler.py | ./scs_dev/osio_mqtt_client.py -e
"""

import json
import random
import sys
import time

from collections import OrderedDict

from scs_dev.cmd.cmd_osio_mqtt_client import CmdOSIOMQTTClient

from scs_core.data.json import JSONify
from scs_core.data.localized_datetime import LocalizedDatetime
from scs_core.data.publication import Publication
from scs_core.osio.client.client_auth import ClientAuth
from scs_core.sys.exception_report import ExceptionReport

from scs_host.client.mqtt_client import MQTTClient
from scs_host.client.mqtt_client import MQTTSubscriber
from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------
# subscription handler...

class OSIOMQTTClient(object):
    """
    classdocs
    """
    # ----------------------------------------------------------------------------------------------------------------

    @classmethod
    def print_publication(cls, pub):
        print(JSONify.dumps(pub))
        sys.stdout.flush()


    @classmethod
    def print_status(cls, status):
        now = LocalizedDatetime.now()
        print("%s:         mqtt: %s" % (now.as_iso8601(), status), file=sys.stderr)
        sys.stderr.flush()


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

        # ClientAuth...
        auth = ClientAuth.load_from_host(Host)

        if auth is None:
            print("ClientAuth not available.", file=sys.stderr)
            exit()

        if cmd.verbose:
            print(auth, file=sys.stderr)

        # client...
        subscriber = None if cmd.topic is None else MQTTSubscriber(cmd.topic, OSIOMQTTClient.print_publication)

        client = MQTTClient(subscriber)
        client.connect(ClientAuth.MQTT_HOST, auth.client_id, auth.user_id, auth.client_password)

        if cmd.verbose:
            print(client, file=sys.stderr)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        # publish loop...
        if cmd.publish:
            for line in sys.stdin:
                try:
                    datum = json.loads(line, object_pairs_hook=OrderedDict)
                except ValueError:
                    if cmd.verbose:
                        OSIOMQTTClient.print_status("bad datum: %s" % line.strip())

                    continue

                while True:
                    publication = Publication.construct_from_jdict(datum)

                    try:
                        if cmd.verbose:
                            OSIOMQTTClient.print_status(datum['payload']['rec'])

                        success = client.publish(publication, ClientAuth.MQTT_TIMEOUT)

                        if cmd.verbose and not success:
                            OSIOMQTTClient.print_status("abandoned")

                        break

                    except Exception as ex:
                        if cmd.verbose:
                            print(JSONify.dumps(ExceptionReport.construct(ex)))
                            sys.stderr.flush()

                    time.sleep(random.uniform(1.0, 2.0))           # Don't hammer the client!

                if cmd.verbose:
                    OSIOMQTTClient.print_status("done")

                if cmd.echo:
                    print(line, end="")
                    sys.stdout.flush()

        # subscribe loop...
        if cmd.topic:
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
