#!/usr/bin/env python3

"""
Created on 7 Oct 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

Requires SystemID and AWS Project documents.

command line example:
./aws_mqtt_client.py south-coast-science-dev/development/device/alpha-bb-eng-000003/control | \
./aws_topic_subscriber.py -t south-coast-science-dev/development/device/alpha-bb-eng-000003/control
"""

import json
import sys

from collections import OrderedDict

from scs_core.data.json import JSONify
from scs_core.data.publication import Publication

from scs_core.aws.config.project import Project

from scs_core.sys.system_id import SystemID
from scs_core.sys.exception_report import ExceptionReport

from scs_dev.cmd.cmd_aws_topic_subscriber import CmdAWSTopicSubscriber

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdAWSTopicSubscriber()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print(cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # topic...
        if cmd.channel:
            # SystemID...
            system_id = SystemID.load(Host)

            if system_id is None:
                print("SystemID not available.", file=sys.stderr)
                exit(1)

            if cmd.verbose:
                print(system_id, file=sys.stderr)

            # Project...
            project = Project.load(Host)

            if project is None:
                print("Project not available.", file=sys.stderr)
                exit(1)

            topic = project.channel_path(cmd.channel, system_id)

        else:
            topic = cmd.topic

        if cmd.verbose:
            print(topic, file=sys.stderr)
            sys.stderr.flush()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        for line in sys.stdin:
            try:
                jdict = json.loads(line, object_pairs_hook=OrderedDict)
            except ValueError:
                continue

            publication = Publication.construct_from_jdict(jdict)

            if publication.topic == topic:
                print(JSONify.dumps(publication.payload))
                sys.stdout.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        if cmd.verbose:
            print("aws_topic_subscriber: KeyboardInterrupt", file=sys.stderr)

    except Exception as ex:
        print(JSONify.dumps(ExceptionReport.construct(ex)), file=sys.stderr)
