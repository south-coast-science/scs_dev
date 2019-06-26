#!/usr/bin/env python3

"""
Created on 23 Jun 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The display utility is used to

SYNOPSIS
display.py [-v]

EXAMPLES
( cat < /home/pi/SCS/pipes/display_pipe & ) | /home/pi/SCS/scs_dev/src/scs_dev/display.py -v

SEE ALSO
scs_mfr/display_conf

RESOURCES
sudo apt install libatlas3-base
sudo apt-get install libopenjp2-7
"""

import sys

from scs_core.display.display_conf import DisplayConf

from scs_core.sys.signalled_exit import SignalledExit

from scs_dev.cmd.cmd_verbose import CmdVerbose

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    cmd = None
    monitor = None

    try:
        # ------------------------------------------------------------------------------------------------------------
        # cmd...

        cmd = CmdVerbose()

        if cmd.verbose:
            print("display: %s" % cmd, file=sys.stderr)


        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # signal handler...
        SignalledExit.construct("display", cmd.verbose)

        # DisplayConf...
        conf = DisplayConf.load(Host)

        if conf is None:
            print("display: DisplayConf not available.", file=sys.stderr)
            exit(1)

        monitor = conf.monitor()

        if cmd.verbose and monitor:
            print("display: %s" % monitor, file=sys.stderr)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        monitor.start()

        for line in sys.stdin:
            message = line.strip()

            if cmd.verbose:
                print("display: %s" % message, file=sys.stderr)
                sys.stderr.flush()

            monitor.set_message(message)


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    finally:
        if monitor:
            monitor.stop()
