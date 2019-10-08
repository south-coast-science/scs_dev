#!/usr/bin/env python3

"""
Created on 18 Nov 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The osio_topic_subscriber utility is used to select subscribed data from the output of the osio_mqtt_client script, and
make it available to a listening process.

The osio_topic_subscriber script is needed because the - given that only one instance per host may be running - the
osio_mqtt_client may be subscribing to multiple topics. The osio_topic_subscriber only responds to one specific
topic. It expects a JSON document of the form provided by osio_mqtt_client. It acts by returning the value of the field
whose field name matches the topic name.

Messaging topics can be specified either by a project channel name, or by an explicit topic path.

SYNOPSIS
osio_topic_subscriber.py { -t TOPIC | -c { C | G | P | S | X } } [-v]

EXAMPLES
( cat ~/SCS/pipes/control_subscription_pipe & ) | ./osio_topic_subscriber.py -cX | ./control_receiver.py -r -v

FILES
~/SCS/osio/osio_project.json
~/SCS/conf/system_id.json

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
scs_dev/osio_mqtt_client
scs_mfr/osio_project
scs_mfr/system_id
"""

import json
import sys

from scs_core.data.json import JSONify
from scs_core.data.publication import Publication

from scs_core.osio.config.project import Project

from scs_core.sys.signalled_exit import SignalledExit
from scs_core.sys.system_id import SystemID

from scs_dev.cmd.cmd_osio_topic_subscriber import CmdOSIOTopicSubscriber

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdOSIOTopicSubscriber()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print("osio_topic_subscriber: %s" % cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # topic...
        if cmd.channel:
            # SystemID...
            system_id = SystemID.load(Host)

            if system_id is None:
                print("osio_topic_subscriber: SystemID not available.", file=sys.stderr)
                exit(1)

            if cmd.verbose:
                print(system_id, file=sys.stderr)

            # Project...
            project = Project.load(Host)

            if project is None:
                print("osio_topic_subscriber: Project not available.", file=sys.stderr)
                exit(1)

            topic = project.channel_path(cmd.channel, system_id)

        else:
            topic = cmd.topic

        # TODO: check if topic exists?

        if cmd.verbose:
            print("osio_topic_subscriber: %s" % topic, file=sys.stderr)
            sys.stderr.flush()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        # signal handler...
        SignalledExit.construct("osio_topic_subscriber", cmd.verbose)

        for line in sys.stdin:
            try:
                jdict = json.loads(line)
            except ValueError:
                continue

            publication = Publication.construct_from_jdict(jdict)

            if publication.topic == topic:
                print(JSONify.dumps(publication.payload))
                sys.stdout.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except (BrokenPipeError, ConnectionResetError) as ex:
        print("osio_topic_subscriber: %s" % ex, file=sys.stderr)

    except SystemExit:
        pass

    finally:
        if cmd and cmd.verbose:
            print("osio_topic_subscriber: finishing", file=sys.stderr)
