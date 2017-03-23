#!/usr/bin/env python3

"""
Created on 23 Mar 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

Requires ClientAuth document.

command line example:
./scs_dev/status_sampler.py | ./scs_dev/mqtt_client.py -e
"""

import json
import random
import sys
import time

from collections import OrderedDict

from scs_core.data.json import JSONify
from scs_core.data.localized_datetime import LocalizedDatetime
from scs_core.data.publication import Publication
from scs_core.osio.client.client_auth import ClientAuth
from scs_core.sys.exception_report import ExceptionReport

from scs_dev.cmd.cmd_mqtt_client import CmdMQTTClient

from scs_host.client.mqtt_client import MQTTClient
from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    client = None

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdMQTTClient()
    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit()

    log_file = open(cmd.log, 'a') if cmd.log else None

    if cmd.verbose:
        print(cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resource...

        auth = ClientAuth.load_from_host(Host)

        if auth is None:
            print("ClientAuth not available.", file=sys.stderr)
            exit()

        if cmd.verbose:
            print(auth, file=sys.stderr)


        client = MQTTClient()
        client.connect(ClientAuth.MQTT_HOST, auth.client_id, auth.username, auth.password)

        if cmd.verbose:
            print(client, file=sys.stderr)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        if cmd.publish:
            for line in sys.stdin:
                datum = json.loads(line, object_pairs_hook=OrderedDict)

                while True:
                    publication = Publication.construct_from_jdict(datum)

                    try:
                        if cmd.log:
                            log_file.write("%s: rec: %s\n" % (LocalizedDatetime.now().as_iso8601(), datum['rec']))
                            log_file.flush()

                        success = client.publish(publication.topic, publication.payload, ClientAuth.MQTT_TIMEOUT)

                        if cmd.log and not success:
                            log_file.write("%s: abandoned")
                            log_file.flush()

                        break

                    except Exception as ex:
                        if cmd.log:
                            report = JSONify.dumps(ExceptionReport.construct(ex))
                            log_file.write("%s\n" % report)
                            log_file.flush()

                    time.sleep(random.uniform(1.0, 2.0))           # Don't hammer the MQTT client!

                if cmd.log:
                    log_file.write("%s: done\n" % LocalizedDatetime.now().as_iso8601())
                    log_file.write("-\n")
                    log_file.flush()

                if cmd.echo:
                    print(line, end="")
                    sys.stdout.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt as ex:
        if cmd.verbose:
            print("mqtt_publisher: KeyboardInterrupt", file=sys.stderr)

    except Exception as ex:
        if cmd.log:
            report = JSONify.dumps(ExceptionReport.construct(ex))
            log_file.write("%s: %s\n" % (LocalizedDatetime.now().as_iso8601(), report))
            log_file.flush()

        print(JSONify.dumps(ExceptionReport.construct(ex)), file=sys.stderr)

    finally:
        if client:
            client.disconnect()

        if cmd.log:
            log_file.close()
