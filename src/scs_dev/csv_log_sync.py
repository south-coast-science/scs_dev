#!/usr/bin/env python3

"""
Created on 16 Jan 2020

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The csv_log_sync utility is used to extract JSON found from the CSV files created by the csv_logger utility.

The utility is designed to be invoked of device start-up. At this point, csv_log_sync can interrogate the server
in order to determine whether there are any found stored on the device with a more recent 'rec' datetime than the
most recent document on the server. If so, these found can be published before device sensing operations begin.

Documents are found in order of messaging topic, then datetime, with the oldest found found first.

In a typical setting, topic paths and start datetimes are found automatically from the server, an alternate test mode
is provided in which a single topic and start datetime is provided on the command line.

In order to interrogate the server, both an AWS API authentication configuration and system ID must be set. The
csv_log_sync utility is not supported by the Open Sensors data platform.

Note that the csv_log_sync utility is only able to find missing server found at the end of the device timeline -
it is not able to infill gaps within the server data timeline.

SYNOPSIS
csv_log_sync.py { -t TOPIC_NAME -s START | -f } [-n] [-w] [-p UDS_PUB] [-v]

EXAMPLES
./csv_log_sync.py -vfw -p ~/SCS/pipes/mqtt_publication.uds

SEE ALSO
scs_dev/csv_logger
scs_dev/csv_reader
scs_dev/csv_writer
scs_mfr/aws_api_auth
scs_mfr/csv_logger_conf
scs_mfr/system_id

BUGS
For compatibility with AWS DynamoDB, the --nullify flag should be used to convert empty string values to null.
"""

import sys

from scs_core.aws.client.api_auth import APIAuth
from scs_core.aws.manager.byline_manager import BylineManager

from scs_core.csv.csv_log import CSVLog
from scs_core.csv.csv_log_cursor_queue import CSVLogCursorQueue
from scs_core.csv.csv_log_reader import CSVLogReader
from scs_core.csv.csv_logger_conf import CSVLoggerConf

from scs_core.sys.signalled_exit import SignalledExit
from scs_core.sys.system_id import SystemID

from scs_dev.cmd.cmd_csv_log_sync import CmdCSVLogSync

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

        if cmd.verbose:
            print("csv_log_sync: %s" % conf, file=sys.stderr)

        if cmd.fill:
            # APIAuth...
            api_auth = APIAuth.load(Host)

            if api_auth is None:
                print("csv_log_sync: APIAuth not available.", file=sys.stderr)
                exit(1)

            # BylineManager...
            manager = BylineManager(HTTPClient(), api_auth)

            if cmd.verbose:
                print("csv_log_sync: %s" % manager, file=sys.stderr)

            # log...
            for byline in manager.find_bylines_for_device(system_id.message_tag()):
                if byline.topic_name() == cmd.topic_name:
                    log = CSVLog(conf.root_path, cmd.topic_name, system_id.message_tag(), byline.rec.datetime)
                    break

            if log is None:
                if cmd.verbose:
                    print("csv_log_sync: no backlog was found for topic %s" % cmd.topic_name, file=sys.stderr)
                exit(0)

        else:
            # log...
            log = CSVLog(conf.root_path, cmd.topic_name, system_id.message_tag(), cmd.start.datetime)

        sys.stderr.flush()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        # signal handler...
        SignalledExit.construct("csv_log_sync", cmd.verbose)

        # read...
        queue = CSVLogCursorQueue.construct_for_log(log, 'rec')
        reader = CSVLogReader(queue, empty_string_as_null=cmd.nullify, verbose=cmd.verbose)

        reader.run(halt_on_empty_queue=True)


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except (BrokenPipeError, ConnectionResetError) as ex:
        print("csv_log_sync: %s" % ex, file=sys.stderr)

    except (KeyboardInterrupt, SystemExit):
        pass

    finally:
        if cmd and cmd.verbose:
            print("csv_log_sync: finishing", file=sys.stderr)
