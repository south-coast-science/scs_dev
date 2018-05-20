#!/usr/bin/env python3

"""
Created on 20 May 2018

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The disk_usage utility is used to determine free and used space on the specified volume.

SYNOPSIS
node.py [-v] VOLUME

EXAMPLES
./disk_usage.py /etc

DOCUMENT EXAMPLE
{"volume": "/etc", "free": 2375217152, "used": 4958257152, "total": 7710990336}
"""

import sys

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
        exit(1)

    if cmd.verbose:
        print("disk_usage: %s" % cmd, file=sys.stderr)
        sys.stderr.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # run...

    usage = Host.disk_usage(cmd.volume)

    print(JSONify.dumps(usage))

