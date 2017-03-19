#!/usr/bin/env python3

"""
Created on 18 Nov 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

Mey require Publication document.

command line example:
./scs_dev/status_sampler.py | ./scs_dev/osio_topic_publisher.py -e -t /users/southcoastscience-dev/test/json
"""

import json
import random
import sys
import time

from collections import OrderedDict

from scs_core.data.json import JSONify
from scs_core.data.localized_datetime import LocalizedDatetime
from scs_core.osio.client.client_auth import ClientAuth
from scs_core.osio.client.topic_client import TopicClient
from scs_core.osio.config.publication import Publication
from scs_core.sys.device_id import DeviceID
from scs_core.sys.exception_report import ExceptionReport

from scs_dev.cmd.cmd_topic_publisher import CmdTopicPublisher

from scs_host.client.mqtt_client import MQTTClient
from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    publisher = None

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdTopicPublisher()
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

        device_id = DeviceID.load_from_host(Host)

        if device_id is None:
            print("DeviceID not available.", file=sys.stderr)
            exit()

        if cmd.verbose:
            print(device_id, file=sys.stderr)


        if cmd.channel:
            publication = Publication.load_from_host(Host)

            if publication is None:
                print("Publication not available.", file=sys.stderr)
                exit()

            if cmd.channel == 'C':
                topic = publication.climate_topic_path()

            elif cmd.channel == 'G':
                topic = publication.gases_topic_path()

            elif cmd.channel == 'P':
                topic = publication.particulates_topic_path()

            else:
                topic = publication.status_topic_path(device_id)

        else:
            topic = cmd.topic

        if cmd.verbose:
            print(topic, file=sys.stderr)


        client = MQTTClient()
        publisher = TopicClient(client, auth)

        publisher.connect()

        if cmd.verbose:
            print(publisher, file=sys.stderr)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        for line in sys.stdin:
            datum = json.loads(line, object_pairs_hook=OrderedDict)

            while True:
                try:
                    if cmd.log:
                        log_file.write("%s: rec: %s\n" % (LocalizedDatetime.now().as_iso8601(), datum['rec']))
                        log_file.flush()

                    success = publisher.publish(topic, datum)

                    if success:
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
            print("osio_topic_publisher: KeyboardInterrupt", file=sys.stderr)

    except Exception as ex:
        if cmd.log:
            report = JSONify.dumps(ExceptionReport.construct(ex))
            log_file.write("%s: %s\n" % (LocalizedDatetime.now().as_iso8601(), report))
            log_file.flush()

        print(JSONify.dumps(ExceptionReport.construct(ex)), file=sys.stderr)

    finally:
        if publisher:
            publisher.disconnect()

        if cmd.log:
            log_file.close()
