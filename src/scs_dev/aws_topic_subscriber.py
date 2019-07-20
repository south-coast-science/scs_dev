#!/usr/bin/env python3

"""
Created on 7 Oct 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The aws_topic_subscriber utility is used to select subscribed data from the output of the aws_mqtt_client script, and
make it available to a listening process.

The aws_topic_subscriber script is needed because the - given that only one instance per host may be running - the
aws_mqtt_client may be subscribing to multiple topics. The aws_topic_subscriber only responds to one specific
topic. It expects a JSON document of the form provided by aws_mqtt_client. It acts by returning the value of the field
whose field name matches the topic name.

Messaging topics can be specified either by a project channel name, or by an explicit topic path. If a project channel
name is used, the aws_topic_subscriber utility requires system ID and AWS project configurations to be set.

SYNOPSIS
aws_topic_publisher.py { -t TOPIC | -c { C | G | P | S | X } } [-v]

EXAMPLES
( cat ~/SCS/pipes/control_subscription_pipe & ) | ./aws_topic_subscriber.py -cX | ./control_receiver.py -r -v

DOCUMENT EXAMPLE - INPUT
{"south-coast-science-dev/production-test/loc/1/gases":
{"tag": "scs-be2-2", "rec": "2018-04-04T13:05:52.675+00:00",
"val": {"NO2": {"weV": 0.316192, "aeV": 0.310317, "weC": 0.002991, "cnc": 22.6},
"CO": {"weV": 0.286567, "aeV": 0.258941, "weC": 0.043378, "cnc": 181.5},
"SO2": {"weV": 0.263879, "aeV": 0.267942, "weC": -0.01022, "cnc": -12.8},
"H2S": {"weV": 0.209753, "aeV": 0.255191, "weC": -0.031478, "cnc": 11.9},
"sht": {"hmd": 57.0, "tmp": 21.3}}}}

DOCUMENT EXAMPLE - OUTPUT
{"tag": "scs-be2-2", "rec": "2018-04-04T13:05:52.675+00:00",
"val": {"NO2": {"weV": 0.316192, "aeV": 0.310317, "weC": 0.002991, "cnc": 22.6},
"CO": {"weV": 0.286567, "aeV": 0.258941, "weC": 0.043378, "cnc": 181.5},
"SO2": {"weV": 0.263879, "aeV": 0.267942, "weC": -0.01022, "cnc": -12.8},
"H2S": {"weV": 0.209753, "aeV": 0.255191, "weC": -0.031478, "cnc": 11.9},
"sht": {"hmd": 57.0, "tmp": 21.3}}}

SEE ALSO
scs_dev/aws_mqtt_client
scs_mfr/aws_project
scs_mfr/system_id
"""

import json
import sys

from collections import OrderedDict

from scs_core.aws.config.project import Project

from scs_core.data.json import JSONify
from scs_core.data.publication import Publication

from scs_core.sys.signalled_exit import SignalledExit
from scs_core.sys.system_id import SystemID

from scs_dev.cmd.cmd_aws_topic_subscriber import CmdAWSTopicSubscriber

from scs_host.sys.host import Host


# TODO: need to move project handling out of osio, and make it common with aws?

# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdAWSTopicSubscriber()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print("aws_topic_subscriber: %s" % cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # signal handler...
        SignalledExit.construct("aws_topic_subscriber", cmd.verbose)

        # topic...
        if cmd.channel:
            # SystemID...
            system_id = SystemID.load(Host)

            if system_id is None:
                print("aws_topic_subscriber: SystemID not available.", file=sys.stderr)
                exit(1)

            if cmd.verbose:
                print("aws_topic_subscriber: %s" % system_id, file=sys.stderr)

            # Project...
            project = Project.load(Host)

            if project is None:
                print("aws_topic_subscriber: Project not available.", file=sys.stderr)
                exit(1)

            topic = project.channel_path(cmd.channel, system_id)

        else:
            topic = cmd.topic

        if cmd.verbose:
            print("aws_topic_subscriber: %s" % topic, file=sys.stderr)
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

    except (BrokenPipeError, ConnectionResetError):
        pass

    finally:
        if cmd.verbose:
            print("aws_topic_subscriber: finishing", file=sys.stderr)
