#!/usr/bin/env python3

"""
Created on 18 Nov 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

https://opensensorsio.helpscoutdocs.com/article/84-overriding-timestamp-information-in-message-payload

Requires SystemID and Project documents.

command line example:
./scs_dev/status_sampler.py | ./scs_dev/osio_topic_publisher.py -e -t /users/southcoastscience-dev/test/json
"""

import json
import sys

from collections import OrderedDict

from scs_core.data.json import JSONify
from scs_core.data.publication import Publication
from scs_core.osio.config.project import Project
from scs_core.sys.system_id import SystemID
from scs_core.sys.exception_report import ExceptionReport

from scs_dev.cmd.cmd_topic_publisher import CmdTopicPublisher

from scs_host.sys.host import Host


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
        # resources...

        # SystemID...
        system_id = SystemID.load_from_host(Host)

        if system_id is None:
            print("SystemID not available.", file=sys.stderr)
            exit()

        if cmd.verbose:
            print(system_id, file=sys.stderr)


        if cmd.channel:
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

            else:
                topic = project.status_topic_path(system_id)

        else:
            topic = cmd.topic

        if cmd.verbose:
            print(topic, file=sys.stderr)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        for line in sys.stdin:
            datum = json.loads(line, object_pairs_hook=OrderedDict)

            if cmd.override:
                payload = OrderedDict({'__timestamp': datum['rec']})
                payload.update(datum)

            else:
                payload = datum

            # time.sleep(1)

            publication = Publication(topic, payload)

            print(JSONify.dumps(publication))
            sys.stdout.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt as ex:
        if cmd.verbose:
            print("osio_topic_publisher: KeyboardInterrupt", file=sys.stderr)

    except Exception as ex:
        print(JSONify.dumps(ExceptionReport.construct(ex)), file=sys.stderr)
