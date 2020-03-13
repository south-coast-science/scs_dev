#!/usr/bin/env python3

"""
Created on 16 Jan 2020

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The csv_log_sync utility is used to extract JSON found from the CSV files created by the csv_logger utility.

The utility can interrogate the server in order to determine whether there are any found stored on the device with a
more recent 'rec' datetime than the most recent document on the server. If so, these found can be published before
device sensing operations begin. An alternate test mode is provided in which a single topic and start datetime is
provided on the command line.

Documents are found in order of datetime, with the oldest found found first.

In order to interrogate the server, both an AWS API authentication configuration and system ID must be set. If the
topic is not supplied as an absolute path, the AWS project must also be set. The csv_log_sync utility is not supported
by the Open Sensors data platform.

Note that the csv_log_sync utility is only able to find missing server found at the end of the device timeline -
it is not able to infill gaps within the server data timeline.

SYNOPSIS
csv_log_sync.py { -s START | -f } [-n] [-a] [-v] TOPIC

EXAMPLES
./csv_log_sync.py  -vf climate

SEE ALSO
scs_dev/csv_logger
scs_dev/csv_reader
scs_dev/csv_writer
scs_mfr/aws_api_auth
scs_mfr/aws_project
scs_mfr/csv_logger_conf
scs_mfr/system_id

BUGS
For compatibility with AWS DynamoDB, the --nullify flag should be used to convert empty string values to null.
"""

import sys

from scs_core.aws.client.api_auth import APIAuth
from scs_core.aws.config.project import Project
from scs_core.aws.manager.byline_manager import BylineManager

from scs_core.csv.csv_log_reader import CSVLogReader
from scs_core.csv.csv_logger_conf import CSVLoggerConf

from scs_core.sys.signalled_exit import SignalledExit
from scs_core.sys.system_id import SystemID

from scs_dev.cmd.cmd_csv_log_sync import CmdCSVLogSync
from scs_dev.handler.csv_log_reporter import CSVLogReporter

from scs_host.client.http_client import HTTPClient
from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    cmd = None
    log = None
    reader = None

    try:
        # ------------------------------------------------------------------------------------------------------------
        # cmd...

        cmd = CmdCSVLogSync()

        if not cmd.is_valid():
            cmd.print_help(sys.stderr)
            exit(2)

        if cmd.verbose:
            print("csv_log_sync: %s" % cmd, file=sys.stderr)


        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # SystemID...
        system_id = SystemID.load(Host)

        if system_id is None:
            print("csv_log_sync: SystemID not available.", file=sys.stderr)
            exit(1)

        if cmd.verbose:
            print("csv_log_sync: %s" % system_id, file=sys.stderr)

        # CSVLoggerConf...
        conf = CSVLoggerConf.load(Host)

        if conf is None:
            print("csv_log_sync: CSVLoggerConf not available.", file=sys.stderr)
            exit(1)

        if cmd.fill:
            # topic...
            if cmd.absolute:
                topic = cmd.topic

            else:
                # Project...
                project = Project.load(Host)

                if project is None:
                    print("csv_log_sync: Project not available.", file=sys.stderr)
                    exit(1)

                topic = project.subject_path(cmd.topic, system_id)

                if topic is None:
                    print("csv_log_sync: no topic found for subject '%s'." % cmd.topic, file=sys.stderr)
                    exit(2)

                if cmd.verbose:
                    print("csv_log_sync (%s): topic: %s" % (cmd.topic, topic), file=sys.stderr)

            # APIAuth...
            api_auth = APIAuth.load(Host)

            if api_auth is None:
                print("csv_log_sync: APIAuth not available.", file=sys.stderr)
                exit(1)

            # BylineManager...
            manager = BylineManager(HTTPClient(True), api_auth)

            if cmd.verbose:
                print("csv_log_sync: %s" % manager, file=sys.stderr)

            # log...
            byline = manager.find_byline_for_device_topic(system_id.message_tag(), topic)
            log = conf.csv_log(cmd.topic, tag=system_id.message_tag(), timeline_start=byline.rec.datetime)

            if log is None:
                if cmd.verbose:
                    print("csv_log_sync: no backlog was found for topic %s" % cmd.topic, file=sys.stderr)
                exit(0)

        else:
            # log...
            log = conf.csv_log(cmd.topic, tag=system_id.message_tag(), timeline_start=cmd.start.datetime)

        # CSVLogReporter...
        reporter = CSVLogReporter('csv_log_sync', cmd.topic, cmd.verbose)

        sys.stderr.flush()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        # signal handler...
        SignalledExit.construct("csv_log_sync", cmd.verbose)

        # read...
        report_file = sys.stderr if cmd.verbose else None
        reader = CSVLogReader(log.cursor_queue('rec'), empty_string_as_null=cmd.nullify, reporter=reporter)

        reader.run(halt_on_empty_queue=True)


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except ConnectionError as ex:
        print("csv_log_sync: %s" % ex, file=sys.stderr)

    except (KeyboardInterrupt, SystemExit):
        pass

    finally:
        if cmd and cmd.verbose:
            print("csv_log_sync: finishing", file=sys.stderr)
