#!/usr/bin/env python3

"""
Created on 15 Oct 2020

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The disk_volume utility is used to determine whether a volume is mounted and, if so, the free and used space on
the volume. Space is given in blocks. The volume is identified by its mount point.

If the "is-available" field in the report is false, this indicates that an OS error occurred when
an attempt was made to access the volume. This error can occur if a removable medium failed, or
was disconnected without being unmounted.

The disk_volume utility is normally included in the commands accepted by the control_receiver utility.

SYNOPSIS
disk_volume.py [-v] MOUNTED_ON

EXAMPLES
./disk_volume.py -v /srv/SCS_logging

DOCUMENT EXAMPLE
{"filesystem": "/dev/mmcblk0p1", "size": 15384184, "used": 319296, "free": 14892092,
"mounted-on": "/srv/SCS_logging", "is-available": false}

SEE ALSO
scs_dev/disk_usage
"""

import sys

from scs_core.data.json import JSONify

from scs_dev.cmd.cmd_disk_volume import CmdDiskVolume

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdDiskVolume()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print("disk_volume: %s" % cmd, file=sys.stderr)
        sys.stderr.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # run...

    volume = Host.disk_volume(cmd.mounted_on)
    print(JSONify.dumps(volume))


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    if cmd.verbose and volume:
        print("percent used: %s" % volume.percent_used(), file=sys.stderr)
