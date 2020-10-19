#!/usr/bin/env python3

"""
Created on 20 May 2018

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The disk_usage utility is used to determine whether a volume is mounted and, if so, the free and used space on
the volume. Space is given in blocks. The volume is identified by any filesystem path within the volume. If the
--csv flag is used, the path is as specified by scs_mfr/csv_logger_conf.

If the "is-available" field in the report is false, this indicates that an OS error occurred when an attempt was
made to access the volume. This error can occur if a removable medium failed, or was disconnected without being
unmounted.

The disk_usage utility is normally included in the commands accepted by the control_receiver utility.

SYNOPSIS
disk_usage.py [-v] { -c | PATH }

EXAMPLES
./disk_usage.py -v /srv/removable_data_storage

DOCUMENT EXAMPLE
{"path": "/srv/removable_data_storage", "free": 15423610880, "used": 329793536, "total": 15753404416,
"is-available": true}

SEE ALSO
scs_dev/disk_volume
"""

import sys

from scs_core.csv.csv_logger_conf import CSVLoggerConf
from scs_core.data.json import JSONify

from scs_dev.cmd.cmd_disk_usage import CmdDiskUsage

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdDiskUsage()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print("disk_usage: %s" % cmd, file=sys.stderr)


    # ----------------------------------------------------------------------------------------------------------------
    # resources...

    # CSVLoggerConf...
    if cmd.csv:
        conf = CSVLoggerConf.load(Host)

        if conf is None:
            print("disk_usage: CSVLoggerConf not available.", file=sys.stderr)
            exit(1)

        if cmd.verbose:
            print("disk_usage: %s" % conf, file=sys.stderr)

    else:
        conf = None


    # ----------------------------------------------------------------------------------------------------------------
    # run...

    path = conf.root_path if cmd.csv else cmd.path

    usage = Host.disk_usage(path)
    print(JSONify.dumps(usage))


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    if cmd.verbose and usage:
        print("disk_usage: percent used: %s" % usage.percent_used(), file=sys.stderr)
