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

import signal
import sys

from scs_core.display.display_conf import DisplayConf

from scs_dev.cmd.cmd_verbose import CmdVerbose

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

def signalled_exit(signum, _):
    if signum == signal.SIGINT:
        signal.signal(signal.SIGINT, ORIGINAL_SIGINT)

        if cmd.verbose:
            print("display: SIGINT", file=sys.stderr)

        sys.exit(1)

    if signum == signal.SIGTERM:
        signal.signal(signal.SIGTERM, signal.SIG_IGN)

        if cmd.verbose:
            print("display: SIGTERM", file=sys.stderr)

        sys.exit(0)


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    cmd = None
    monitor = None

    ORIGINAL_SIGINT = signal.getsignal(signal.SIGINT)

    signal.signal(signal.SIGINT, signalled_exit)
    signal.signal(signal.SIGTERM, signalled_exit)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # cmd...

        cmd = CmdVerbose()

        if cmd.verbose:
            print("display: %s" % cmd, file=sys.stderr)


        # ------------------------------------------------------------------------------------------------------------
        # resources...

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
