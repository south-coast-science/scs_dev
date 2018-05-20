#!/usr/bin/env python3

"""
Created on 20 May 2018

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The disk_usage utility is used to determine free and used space on the specified volume. The volume is identified by
any filesystem path within the volume.

The disk_usage utility is normally included in the commands accepted by the control_receiver utility.

SYNOPSIS
disk_usage.py [-v] VOLUME

EXAMPLES
./disk_usage.py /srv/removable_data_storage

DOCUMENT EXAMPLE
{"volume": "/srv/removable_data_storage", "free": 2375217152, "used": 4958257152, "total": 7710990336}
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

