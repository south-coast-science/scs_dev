#!/usr/bin/env python3

"""
Created on 18 Nov 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

command line example:
./scs_dev/status_sampler.py | ./scs_dev/osio_topic_publisher.py -e /users/southcoastscience-dev/test/json
"""

import json
import sys

from collections import OrderedDict

from scs_core.data.json import JSONify
from scs_core.osio.client.client_auth import ClientAuth
from scs_core.osio.client.topic_client import TopicClient
from scs_core.sys.exception_report import ExceptionReport

from scs_dev.cmd.cmd_topic_publisher import CmdTopicPublisher

from scs_host.client.mqtt_client import MQTTClient
from scs_host.sys.host import Host


# TODO: make this work with HTTP PUT

# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdTopicPublisher()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit()

    if cmd.verbose:
        print(cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resource...

        client = MQTTClient()
        auth = ClientAuth.load_from_host(Host)

        publisher = TopicClient(client, auth)

        if cmd.verbose:
            print(publisher, file=sys.stderr)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        for line in sys.stdin:
            datum = json.loads(line, object_pairs_hook=OrderedDict)
            publisher.publish(cmd.topic, datum)

            if cmd.echo:
                print(line, end="")
                sys.stdout.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt as ex:
        if cmd.verbose:
            print("osi_topic_publisher: KeyboardInterrupt", file=sys.stderr)

    except Exception as ex:
        print(JSONify.dumps(ExceptionReport.construct(ex)), file=sys.stderr)
