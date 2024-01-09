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

Note: echoing cannot begin until a network connection has been established.

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
scs_mfr/aws_project
scs_mfr/csv_logger_conf
scs_mfr/system_id

BUGS
If any filesystem problem is encountered then the reader child process is stopped, and the utility directly echoes
stdin to stdout from then on. No attempt is made to restart the reader process.
"""

import sys
import time

from requests.exceptions import ConnectionError

from scs_core.aws.config.project import Project

from scs_core.aws.security.cognito_device import CognitoDeviceCredentials
from scs_core.aws.security.cognito_login_manager import CognitoLoginManager

from scs_core.csv.csv_log_reader import CSVLogReader, CSVLogQueueBuilder
from scs_core.csv.csv_logger import CSVLogger
from scs_core.csv.csv_logger_conf import CSVLoggerConf

from scs_core.sys.logging import Logging
from scs_core.sys.signalled_exit import SignalledExit
from scs_core.sys.system_id import SystemID

from scs_dev.cmd.cmd_csv_logger import CmdCSVLogger

from scs_host.sys.host import Host


# TODO: Jan  9 09:41:18 scs-bbe-904 sh[854]: csv_logger (particulates):
#  AttributeError("'NoneType' object has no attribute 'free'")
# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    cmd = None
    auth = None
    logger = None
    writer = None
    reader = None
    file_path = None

    try:
        # ------------------------------------------------------------------------------------------------------------
        # cmd...

        cmd = CmdCSVLogger()

        if not cmd.is_valid():
            cmd.print_help(sys.stderr)
            exit(2)

        # logging...
        Logging.config('csv_logger (%s)' % cmd.topic, verbose=cmd.verbose)
        logger = Logging.getLogger()

        logger.info(cmd)


        # ------------------------------------------------------------------------------------------------------------
        # authentication...

        credentials = CognitoDeviceCredentials.load_credentials_for_device(Host)

        gatekeeper = CognitoLoginManager()


        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # SystemID...
        system_id = SystemID.load(Host)

        if system_id is None:
            logger.error("SystemID not available.")
            exit(1)

        # CSVLoggerConf...
        conf = CSVLoggerConf.load(Host)

        if conf is None:
            logger.error("CSVLoggerConf not available.")
            exit(1)

        # writer...
        write_log = conf.csv_log(cmd.topic, tag=system_id.message_tag())
        writer = CSVLogger.construct(Host, write_log, conf.delete_oldest, conf.write_interval)

        logger.info(writer)

        # reader...
        if cmd.echo:
            # literal topic...
            if cmd.absolute:
                topic_path = cmd.topic

            else:
                # Project...
                project = Project.load(Host)

                if project is None:
                    logger.error("Project not available.")
                    exit(1)

                topic_path = project.subject_path(cmd.topic, system_id)

                if topic_path is None:
                    logger.error("no topic found for subject.")
                    exit(2)

            # CSVLogQueueBuilder...
            queue_builder = CSVLogQueueBuilder(conf, credentials, system_id.message_tag(), cmd.topic, topic_path)

            # CSVLogReader...
            reader = CSVLogReader(queue_builder, nullify=True)

            logger.info(reader)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        # signal handler...
        SignalledExit.construct()

        # start reader...
        if cmd.echo:
            reader.start()

        for line in sys.stdin:
            # write...
            jstr = line.strip()

            if jstr is None:
                break

            try:
                for i in range(5):
                    try:
                        file_path = writer.write(jstr)
                        break

                    except TimeoutError:
                        time.sleep(1)

                        if i < 4:
                            continue

                        raise TimeoutError("multiple write attempts failed")

            except Exception as ex:
                logger.error(repr(ex))
                writer.writing_inhibited = True

                if reader:
                    reader.stop()

            if not cmd.echo and not writer.writing_inhibited:
                continue

            # direct echo...
            if writer.writing_inhibited:
                logger.error("no CSV access")

                print(jstr)
                sys.stdout.flush()

                continue

            # manage reader...
            reader.include(file_path)


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except ConnectionError as ex:
        logger.error(repr(ex))

    except (KeyboardInterrupt, SystemExit):
        pass

    finally:
        if cmd:
            logger.info("finishing")

        if writer:
            writer.close()

        if reader:
            reader.stop()
