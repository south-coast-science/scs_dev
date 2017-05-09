#!/usr/bin/env python3

"""
Created on 18 Nov 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

https://opensensorsio.helpscoutdocs.com/article/84-overriding-timestamp-information-in-message-payload

Requires SystemID and Project documents.

command line example:
./osio_mqtt_client.py /orgs/south-coast-science-dev/development/device/alpha-bb-eng-000003/control | \
./osio_topic_subscriber.py -cX
"""

import json
import sys

from collections import OrderedDict

from scs_core.data.json import JSONify
from scs_core.data.publication import Publication
from scs_core.osio.config.project import Project
from scs_core.sys.system_id import SystemID
from scs_core.sys.exception_report import ExceptionReport

from scs_dev.cmd.cmd_topic_subscriber import CmdTopicSubscriber

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdTopicSubscriber()
    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit()

    if cmd.verbose:
        print(cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # topic...
        if cmd.channel:
            # SystemID...
            system_id = SystemID.load_from_host(Host)

            if system_id is None:
                print("SystemID not available.", file=sys.stderr)
                exit()

            if cmd.verbose:
                print(system_id, file=sys.stderr)

            # Project...
            project = Project.load_from_host(Host)

            if project is None:
                print("Project not available.", file=sys.stderr)
                exit()

            if cmd.channel == 'C':
                topic = project.climate_topic_path()

            elif cmd.channel == 'G':
                topic = project.gases_topic_path()

            elif cmd.channel == 'P':
                topic = project.particulates_topic_path()

            elif cmd.channel == 'S':
                topic = project.status_topic_path(system_id)

            elif cmd.channel == 'X':
                topic = project.control_topic_path(system_id)

            else:
                raise ValueError("osio_topic_subscriber: unrecognised channel: %s" % cmd.channel)

        else:
            topic = cmd.topic

        # TODO: check if topic exists

        if cmd.verbose:
            print(topic, file=sys.stderr)
            sys.stderr.flush()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        for line in sys.stdin:
            jdict = json.loads(line, object_pairs_hook=OrderedDict)

            publication = Publication.construct_from_jdict(jdict)

            if publication.topic == topic:
                print(JSONify.dumps(publication.payload))
                sys.stdout.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt as ex:
        if cmd.verbose:
            print("osio_topic_subscriber: KeyboardInterrupt", file=sys.stderr)

    except Exception as ex:
        print(JSONify.dumps(ExceptionReport.construct(ex)), file=sys.stderr)
