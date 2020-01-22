#!/usr/bin/env python3

"""
Created on 16 Jan 2020

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The csv_log_sync utility is used to extract JSON found from the CSV files created by the csv_logger utility.

The utility is designed to be invoked of device start-up. At this point, csv_log_sync can interrogate the server
in order to determine whether there are any found stored on the device with a more recent 'rec' datetime than the
most recent document on the server. If so, these found can be published before device sensing operations begin.

Documents are found in order of messaging topic, then datetime, with the oldest found found first. Documents
are output to stdout by default, but may be written to a Unix domain socket, allowing simple integration with the
aws_mqtt_client message publishing utility.

In a typical setting, topic paths and start datetimes are found automatically from the server, an alternate test mode
is provided in which a single topic and start datetime is provided on the command line.

A --wrapper flag is provided to indicate that each document should be wrapped with a field name identifying the
full topic path, as is done by the aws_topic_publisher.py utility.

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

import json
import sys

from collections import OrderedDict

from scs_core.aws.client.api_auth import APIAuth
from scs_core.aws.manager.byline_manager import BylineManager

from scs_core.csv.csv_log import CSVLog
from scs_core.csv.csv_logger_conf import CSVLoggerConf
from scs_core.csv.csv_reader import CSVReader, CSVReaderException

from scs_core.csv.csv_log_cursor import CSVLogCursorQueue

from scs_core.data.json import JSONify
from scs_core.data.publication import Publication

from scs_core.sys.signalled_exit import SignalledExit
from scs_core.sys.system_id import SystemID

from scs_dev.cmd.cmd_csv_log_sync import CmdCSVLogSync
from scs_dev.handler.uds_writer import UDSWriter

from scs_host.client.http_client import HTTPClient
from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    cmd = None
    reader = None

    file_count = 0
    topic_found = 0
    total_found = 0

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

        # CSVLoggerConf...
        conf = CSVLoggerConf.load(Host)

        if conf is None:
            print("csv_log_sync: CSVLoggerConf not available.", file=sys.stderr)
            exit(1)

        if cmd.verbose:
            print("csv_log_sync: %s" % conf, file=sys.stderr)

        if cmd.topic_name:
            logs = {cmd.topic_name: CSVLog(conf.root_path, cmd.topic_name, None, cmd.start.datetime)}

        else:
            # SystemID...
            system_id = SystemID.load(Host)

            if system_id is None:
                print("csv_log_sync: SystemID not available.", file=sys.stderr)
                exit(1)

            if cmd.verbose:
                print("csv_log_sync: %s" % system_id, file=sys.stderr)

            # APIAuth...
            api_auth = APIAuth.load(Host)

            if api_auth is None:
                print("csv_log_sync: APIAuth not available.", file=sys.stderr)
                exit(1)

            # BylineManager...
            manager = BylineManager(HTTPClient(), api_auth)

            if cmd.verbose:
                print("csv_log_sync: %s" % manager, file=sys.stderr)

            # Bylines...
            logs = {}
            for byline in manager.find_bylines_for_device(system_id.message_tag()):
                logs[byline.topic] = CSVLog(conf.root_path, byline.topic_name(), None, byline.rec.datetime)

        # comms...
        writer = UDSWriter(cmd.uds_pub)

        if cmd.verbose and cmd.uds_pub:
            print("csv_log_sync: %s" % writer, file=sys.stderr)

        sys.stderr.flush()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        # signal handler...
        SignalledExit.construct("csv_log_sync", cmd.verbose)

        for topic, log in logs.items():
            # CSVLogCursorQueue...
            cursor_queue = CSVLogCursorQueue.construct_for_log(log, 'rec')

            if cmd.verbose:
                print("csv_log_sync: topic: %s" % topic, file=sys.stderr)
                sys.stderr.flush()

            topic_found = 0

            # files...
            for cursor in cursor_queue.cursors():
                if cmd.verbose:
                    print("csv_log_sync: %s" % cursor, file=sys.stderr)
                    sys.stderr.flush()

                reader = CSVReader.construct_for_file(cursor.file_path, start_row=cursor.row_number,
                                                      empty_string_as_null=cmd.nullify)
                file_count += 1
                found = 0

                try:
                    # found...
                    for row in reader.rows():
                        datum = json.loads(row, object_pairs_hook=OrderedDict)

                        if cmd.wrapper:
                            publication = Publication(topic, datum)
                            jdict = publication.as_json()
                        else:
                            jdict = datum

                        try:
                            writer.connect()
                            writer.write(JSONify.dumps(jdict))

                        finally:
                            writer.close()

                        found += 1

                    print("csv_log_sync: found: %d" % found, file=sys.stderr)
                    sys.stderr.flush()

                except CSVReaderException as ex:
                    if cmd.verbose:
                        print("csv_log_sync: abandoning file: %s" % ex, file=sys.stderr)
                        sys.stderr.flush()
                        continue

                finally:
                    reader.close()

                topic_found += found
                total_found += found

            print("csv_log_sync: %s: found: %d" % (log.topic_name, topic_found), file=sys.stderr)
            sys.stderr.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except (BrokenPipeError, ConnectionResetError) as ex:
        print("csv_log_sync: %s" % ex, file=sys.stderr)

    except (KeyboardInterrupt, SystemExit):
        pass

    finally:
        if cmd and cmd.verbose and file_count > 1:
            print("csv_log_sync: total files: %s total found: %d" % (file_count, total_found), file=sys.stderr)

        if cmd and cmd.verbose:
            print("csv_log_sync: finishing", file=sys.stderr)
