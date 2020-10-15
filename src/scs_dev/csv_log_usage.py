#!/usr/bin/env python3

"""
Created on 15 Oct 2020

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The csv_log_usage utility is used to determine free and used space on the volume specified by
scs_mfr/csv_logger_conf. Space is given in bytes.

The csv_log_usage utility is normally included in the commands accepted by the control_receiver utility.

SYNOPSIS
csv_log_usage.py [-v]

EXAMPLES
./csv_log_usage.py -v

DOCUMENT EXAMPLE
{"path": "/srv/removable_data_storage", "free": 15424450560, "used": 328953856, "total": 15753404416,
"is-available": true}

SEE ALSO
scs_dev/disk_usage
scs_mfr/csv_logger_conf

"""

import sys

from scs_core.csv.csv_logger_conf import CSVLoggerConf
from scs_core.data.json import JSONify

from scs_dev.cmd.cmd_verbose import CmdVerbose

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdVerbose()

    if cmd.verbose:
        print("csv_log_usage: %s" % cmd, file=sys.stderr)


    # ----------------------------------------------------------------------------------------------------------------
    # resources...

    # CSVLoggerConf...
    conf = CSVLoggerConf.load(Host)

    if conf is None:
        print("csv_log_usage: CSVLoggerConf not available.", file=sys.stderr)
        exit(1)

    if cmd.verbose:
        print("csv_log_usage: %s" % conf, file=sys.stderr)


    # ----------------------------------------------------------------------------------------------------------------
    # run...

    usage = Host.disk_usage(conf.root_path)
    print(JSONify.dumps(usage))


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    if cmd.verbose and usage:
        print("csv_log_usage: percent used: %s" % usage.percent_used(), file=sys.stderr)
