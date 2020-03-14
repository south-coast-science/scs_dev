#!/usr/bin/env python3

"""
Created on 16 Apr 2018

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The csv_logger utility is used to provide continuous logging of data. For devices that are not internet-connected, this
can be used as the method of data capture. For always-connected devices, it is recommended that the utility is used to
provide a backup facility. This is because, in normal operations, data that is queued for publishing is held in
volatile memory.

The operation of the csv_logger is specified using the csv_logger_conf utility - this specifies the filesystem location
for logging, together with the logging mode of operation.

The csv_logger receives JSON data on stdin and writes this to the log file. The log file is named for its topic and the
date / time of the first JSON document reception. Log files are closed - and a new log file opened - each day after
00:00 UTC. All logging date / times are UTC, irrespective of the system or application timezone. Log files are stored in
directories named for the year and month.

If the system ID is set (using the scs_mfr/system_id utility) then log files are prepended with the device tag.
Otherwise, the log file name begins with the date / time.

Like the csv_writer utility, the csv_logger converts data from JSON format to comma-separated value (CSV) format.
The path into the JSON document is used to name the column in the header row, with JSON nodes separated by a period
('.') character.

All the leaf nodes of the first JSON document are included in the CSV. If subsequent JSON documents in the input stream
contain fields that were not in this first document, these extra fields are ignored.

If the --echo flag is used, then the csv_logger utility writes the received data to stdout. When the utility starts,
the historic data API is queried to find the most recent record for the topic. The log reader child process then
outputs any data on the device that is missing from the data store before outputting new records. Valid AWS API
credentials and configuration are required.

Note: this utility waits forever for a network connection and domain name server.

SYNOPSIS
csv_logger.py [-a] [-e] [-v] TOPIC

EXAMPLES
./socket_receiver.py | ./csv_logger.py -e climate

DOCUMENT EXAMPLE - INPUT
{"tag": "scs-ap1-6", "rec": "2018-04-04T14:50:27.641+00:00", "val": {"hmd": 59.6, "tmp": 23.8}}

DOCUMENT EXAMPLE - FILE CONTENTS
tag,rec,val.hmd,val.tmp
scs-ap1-6,2018-04-04T14:50:38.394+00:00,59.7,23.8

SEE ALSO
scs_dev/csv_log_sync
scs_dev/csv_reader
scs_dev/csv_writer
scs_mfr/aws_api_auth
scs_mfr/aws_project
scs_mfr/csv_logger_conf
scs_mfr/system_id

BUGS
If any filesystem problem is encountered then both logging and output are inhibited, and no further attempt is made to
re-establish access to the storage medium.
"""

import sys

from scs_core.aws.client.api_auth import APIAuth
from scs_core.aws.config.project import Project
from scs_core.aws.manager.byline_manager import BylineManager

from scs_core.csv.csv_log_reader import CSVLogReader
from scs_core.csv.csv_logger import CSVLogger
from scs_core.csv.csv_logger_conf import CSVLoggerConf

from scs_core.sys.signalled_exit import SignalledExit
from scs_core.sys.system_id import SystemID

from scs_dev.cmd.cmd_csv_logger import CmdCSVLogger
from scs_dev.handler.csv_log_reporter import CSVLogReporter

from scs_host.client.http_client import HTTPClient
from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    cmd = None
    writer = None
    reader = None

    try:
        # ------------------------------------------------------------------------------------------------------------
        # cmd...

        cmd = CmdCSVLogger()

        if not cmd.is_valid():
            cmd.print_help(sys.stderr)
            exit(2)

        if cmd.verbose:
            print("csv_logger (%s): %s" % (cmd.topic, cmd), file=sys.stderr)


        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # SystemID...
        system_id = SystemID.load(Host)

        if system_id is None:
            print("csv_logger (%s): SystemID not available." % cmd.topic, file=sys.stderr)
            exit(1)

        # CSVLoggerConf...
        conf = CSVLoggerConf.load(Host)

        if conf is None:
            print("csv_logger (%s): CSVLoggerConf not available." % cmd.topic, file=sys.stderr)
            exit(1)

        # writer...
        write_log = conf.csv_log(cmd.topic, tag=system_id.message_tag())
        writer = CSVLogger(Host, write_log, conf.delete_oldest, conf.write_interval)

        if cmd.verbose:
            print("csv_logger (%s): %s" % (cmd.topic, writer), file=sys.stderr)

        # topic...
        if cmd.absolute:
            topic = cmd.topic

        else:
            # Project...
            project = Project.load(Host)

            if project is None:
                print("csv_logger: Project not available.", file=sys.stderr)
                exit(1)

            topic = project.subject_path(cmd.topic, system_id)

            if topic is None:
                print("csv_logger: no topic found for subject '%s'." % cmd.topic, file=sys.stderr)
                exit(2)

            if cmd.verbose:
                print("csv_logger (%s): topic: %s" % (cmd.topic, topic), file=sys.stderr)

        # reader...
        if cmd.echo:
            # APIAuth...
            api_auth = APIAuth.load(Host)

            if api_auth is None:
                print("csv_logger (%s): APIAuth not available." % cmd.topic, file=sys.stderr)
                exit(1)

            # BylineManager...
            manager = BylineManager(HTTPClient(True), api_auth)

            # CSVLogReader...
            byline = manager.find_byline_for_device_topic(system_id.message_tag(), topic)
            timeline_start = None if byline is None else byline.rec.datetime

            if cmd.verbose:
                print("csv_logger (%s): timeline_start: %s" % (cmd.topic, timeline_start), file=sys.stderr)
                sys.stderr.flush()

            reporter = CSVLogReporter("csv_logger", cmd.topic, cmd.verbose)

            read_log = conf.csv_log(cmd.topic, tag=system_id.message_tag(), timeline_start=timeline_start)
            reader = CSVLogReader(read_log.cursor_queue('rec'), empty_string_as_null=True, reporter=reporter)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        # signal handler...
        SignalledExit.construct("csv_logger (%s)" % cmd.topic, cmd.verbose)

        # log reader...
        if cmd.echo:
            reader.start()

        # log writer...
        for line in sys.stdin:
            jstr = line.strip()

            if jstr is None:
                break

            try:
                file_path = writer.write(jstr)

                if cmd.echo:
                    reader.include(file_path)

            except OSError as ex:
                writer.writing_inhibited = True
                print("csv_logger (%s): %s" % (cmd.topic, ex), file=sys.stderr)
                sys.stderr.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except (ConnectionError, RuntimeError) as ex:
        print("csv_logger (%s): %s" % (cmd.topic, ex), file=sys.stderr)

    except (KeyboardInterrupt, SystemExit):
        pass

    finally:
        if cmd and cmd.verbose:
            print("csv_logger (%s): finishing" % cmd.topic, file=sys.stderr)

        if writer:
            writer.close()

        if reader:
            reader.stop()
