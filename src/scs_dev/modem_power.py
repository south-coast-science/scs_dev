#!/usr/bin/env python3

"""
Created on 28 Feb 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The modem_power utility is used to apply or remove power to the South Coast Science 2G modem board for BeagleBone.

Note: in some operating system configurations, the modem board is under control of the Debian modem manager. In these
cases, the modem manager may override the operation of this utility. The modem_power utility is not available on
Raspberry Pi systems.

SYNOPSIS
modem_power.py { 1 | 0 } [-v]

EXAMPLES
./modem_power.py 1
"""

import sys

from scs_comms.modem.io import IO

from scs_dev.cmd.cmd_power import CmdPower

from scs_host.bus.i2c import I2C
from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    I2C.open(Host.I2C_SENSORS)

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdPower()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print(cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        io = IO()

        if cmd.verbose:
            print(io, file=sys.stderr)
            sys.stderr.flush()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        if cmd.power:
            # modem...
            io.power = IO.LOW
            io.output_enable = IO.HIGH

        else:
            # modem...
            io.output_enable = IO.LOW
            io.power = IO.HIGH


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    finally:
        I2C.close()
