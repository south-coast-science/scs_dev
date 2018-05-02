#!/usr/bin/env python3

"""
Created on 18 Nov 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The aws_topic_publisher utility is used to prepare data for publication by the aws_mqtt_client script. The
aws_topic_publisher acts by taking data from stdin, wrapping it in a JSON document whose only field has the name of
the given topic, and presenting the result on stdout.

Messaging topics can be specified either by a project channel name, or by an explicit topic path. If a project channel
name is used, the aws_topic_publisher utility requires system ID and AWS project configurations to be set.

SYNOPSIS
aws_topic_publisher.py { -t TOPIC | -c { C | G | P | S | X } } [-v]

EXAMPLES
./control_receiver.py -r -v | ./aws_topic_publisher.py -v -cX > ~/SCS/pipes/mqtt_publication_pipe

FILES
~/SCS/aws/aws_project.json
~/SCS/conf/system_id.json

DOCUMENT EXAMPLE - INPUT
{"tag": "scs-be2-2", "rec": "2018-04-04T13:05:52.675+00:00",
"val": {"NO2": {"weV": 0.316192, "aeV": 0.310317, "weC": 0.002991, "cnc": 22.6},
"CO": {"weV": 0.286567, "aeV": 0.258941, "weC": 0.043378, "cnc": 181.5},
"SO2": {"weV": 0.263879, "aeV": 0.267942, "weC": -0.01022, "cnc": -12.8},
"H2S": {"weV": 0.209753, "aeV": 0.255191, "weC": -0.031478, "cnc": 11.9},
"sht": {"hmd": 57.0, "tmp": 21.3}}}

DOCUMENT EXAMPLE - OUTPUT
{"south-coast-science-dev/production-test/loc/1/gases":
{"tag": "scs-be2-2", "rec": "2018-04-04T13:05:52.675+00:00",
"val": {"NO2": {"weV": 0.316192, "aeV": 0.310317, "weC": 0.002991, "cnc": 22.6},
"CO": {"weV": 0.286567, "aeV": 0.258941, "weC": 0.043378, "cnc": 181.5},
"SO2": {"weV": 0.263879, "aeV": 0.267942, "weC": -0.01022, "cnc": -12.8},
"H2S": {"weV": 0.209753, "aeV": 0.255191, "weC": -0.031478, "cnc": 11.9},
"sht": {"hmd": 57.0, "tmp": 21.3}}}}

SEE ALSO
scs_dev/aws_mqtt_client
scs_mfr/aws_project
scs_mfr/system_id
"""

import json
import sys

from collections import OrderedDict

from scs_core.data.json import JSONify
from scs_core.data.publication import Publication

from scs_core.aws.config.project import Project

from scs_core.sys.system_id import SystemID

from scs_dev.cmd.cmd_aws_topic_publisher import CmdAWSTopicPublisher

from scs_host.sys.host import Host


# TODO: need to move project handling out of osio, and make it common with aws.

# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdAWSTopicPublisher()
    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print("aws_topic_publisher: %s" % cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # topic...
        if cmd.channel:
            # SystemID...
            system_id = SystemID.load(Host)

            if system_id is None:
                print("aws_topic_publisher: SystemID not available.", file=sys.stderr)
                exit(1)

            if cmd.verbose:
                print("aws_topic_publisher: %s" % system_id, file=sys.stderr)

            # Project...
            project = Project.load(Host)

            if project is None:
                print("aws_topic_publisher: Project not available.", file=sys.stderr)
                exit(1)

            topic = project.channel_path(cmd.channel, system_id)

        else:
            topic = cmd.topic

        if cmd.verbose:
            print("aws_topic_publisher: %s" % topic, file=sys.stderr)
            sys.stderr.flush()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        for line in sys.stdin:
            try:
                jdict = json.loads(line, object_pairs_hook=OrderedDict)
            except ValueError:
                continue

            payload = jdict

            publication = Publication(topic, payload)

            print(JSONify.dumps(publication))
            sys.stdout.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        if cmd.verbose:
            print("aws_topic_publisher: KeyboardInterrupt", file=sys.stderr)
