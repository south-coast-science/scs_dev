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

If the "echo" (-e) flag is used, then the csv_logger utility writes the received data to stdout. The csv_logger will
write to stdout irrespective of whether a csv_logger_conf is specified, or whether logging can continue (for example,
because of a filesystem problem).

SYNOPSIS
csv_logger.py [-e] [-v] TOPIC

EXAMPLES
./socket_receiver.py | ./csv_logger.py -e climate

DOCUMENT EXAMPLE - INPUT
{"tag": "scs-ap1-6", "rec": "2018-04-04T14:50:27.641+00:00", "val": {"hmd": 59.6, "tmp": 23.8}}

DOCUMENT EXAMPLE - FILE CONTENTS
tag,rec,val.hmd,val.tmp
scs-ap1-6,2018-04-04T14:50:38.394+00:00,59.7,23.8

SEE ALSO
scs_dev/csv_reader
scs_dev/csv_writer
scs_mfr/csv_logger_conf
scs_mfr/system_id

BUGS
If any filesystem problem is encountered then logging is inhibited, and no further attempt is made to re-establish
access to the storage medium.
"""

import sys

from scs_core.csv.csv_log import CSVLog
from scs_core.csv.csv_logger import CSVLogger
from scs_core.csv.csv_logger_conf import CSVLoggerConf

from scs_core.sys.signalled_exit import SignalledExit
from scs_core.sys.system_id import SystemID

from scs_dev.cmd.cmd_csv_logger import CmdCSVLogger

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    cmd = None
    logger = None

    try:
        # ------------------------------------------------------------------------------------------------------------
        # cmd...

        cmd = CmdCSVLogger()

        if not cmd.is_valid():
            cmd.print_help(sys.stderr)
            exit(2)

        if cmd.verbose:
            print("csv_logger: %s" % cmd, file=sys.stderr)


        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # signal handler...
        SignalledExit.construct("csv_logger", cmd.verbose)

        # SystemID...
        system_id = SystemID.load(Host)

        if system_id and cmd.verbose:
            print("csv_logger: %s" % system_id, file=sys.stderr)

        tag = None if system_id is None else system_id.message_tag()

        # CSVLoggerConf...
        conf = CSVLoggerConf.load(Host)

        if conf and cmd.verbose:
            print("csv_logger: %s" % conf, file=sys.stderr)

        # CSVLog...
        log = None if conf is None else CSVLog(conf.root_path, cmd.topic, tag)

        if log and cmd.verbose:
            print("csv_logger: %s" % log, file=sys.stderr)

        # CSVLogger...
        logger = None if log is None else CSVLogger(Host, log, conf.delete_oldest, conf.write_interval)

        if cmd.verbose:
            print("csv_logger: %s" % logger, file=sys.stderr)
            sys.stderr.flush()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        for line in sys.stdin:
            jstr = line.strip()

            if jstr is None:
                break

            if logger:
                try:
                    logger.write(jstr)

                except OSError as ex:
                    logger.writing_inhibited = True

                    print("csv_logger: %s" % ex, file=sys.stderr)
                    sys.stderr.flush()

            # echo...
            if cmd.echo:
                print(jstr)
                sys.stdout.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except (BrokenPipeError, ConnectionResetError):
        pass

    finally:
        if cmd.verbose:
            print("csv_logger: finishing", file=sys.stderr)

        if logger is not None:
            logger.close()
