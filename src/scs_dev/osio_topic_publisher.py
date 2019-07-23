#!/usr/bin/env python3

"""
Created on 18 Nov 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The osio_topic_publisher utility is used to prepare data for publication by the osio_mqtt_client script. The
osio_topic_publisher acts by taking data from stdin, wrapping it in a JSON document whose only field has the name of
the given topic, and presenting the result on stdout.

Messaging topics can be specified either by a project channel name, or by an explicit topic path. If a project channel
name is used, the osio_topic_publisher utility requires the system ID and AWS project configurations to be set.

In addition to specifying the channel, the osio_topic_publisher utility can instruct the OpenSensors.io server
to override the message reception timestamp.

SYNOPSIS
osio_topic_publisher.py { -t TOPIC | -c { C | G | P | S | X } } [-o] [-v]

EXAMPLES
./control_receiver.py -r -v | ./osio_topic_publisher.py -v -cX > ~/SCS/pipes/mqtt_publication_pipe

FILES
~/SCS/osio/osio_project.json
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
scs_dev/osio_mqtt_client
scs_mfr/osio_project
scs_mfr/system_id

RESOURCES
https://opensensorsio.helpscoutdocs.com/article/84-overriding-timestamp-information-in-message-payload
"""

import json
import sys

from collections import OrderedDict

from scs_core.data.json import JSONify
from scs_core.data.publication import Publication

from scs_core.osio.config.project import Project

from scs_core.sys.signalled_exit import SignalledExit
from scs_core.sys.system_id import SystemID

from scs_dev.cmd.cmd_osio_topic_publisher import CmdOSIOTopicPublisher

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdOSIOTopicPublisher()
    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print("osio_topic_publisher: %s" % cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # signal handler...
        SignalledExit.construct("osio_topic_publisher", cmd.verbose)

        # topic...
        if cmd.channel:
            # SystemID...
            system_id = SystemID.load(Host)

            if system_id is None:
                print("osio_topic_publisher: SystemID not available.", file=sys.stderr)
                exit(1)

            if cmd.verbose:
                print("osio_topic_publisher: %s" % system_id, file=sys.stderr)

            # Project...
            project = Project.load(Host)

            if project is None:
                print("osio_topic_publisher: Project not available.", file=sys.stderr)
                exit(1)

            topic = project.channel_path(cmd.channel, system_id)

        else:
            topic = cmd.topic

        # TODO: check if topic exists?

        if cmd.verbose:
            print("osio_topic_publisher: %s" % topic, file=sys.stderr)
            sys.stderr.flush()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        for line in sys.stdin:
            try:
                jdict = json.loads(line)
            except ValueError:
                continue

            if cmd.override:
                payload = OrderedDict({'__timestamp': jdict['rec']})
                payload.update(jdict)

            else:
                payload = jdict

            publication = Publication(topic, payload)

            print(JSONify.dumps(publication))
            sys.stdout.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except (BrokenPipeError, ConnectionResetError):
        pass

    finally:
        if cmd and cmd.verbose:
            print("osio_topic_publisher: finishing", file=sys.stderr)
