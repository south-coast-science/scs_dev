#!/usr/bin/env python3

"""
Created on 28 Feb 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

command line example:
./modem_power.py -v 0
"""

import sys

from scs_comms.modem.io import IO

from scs_core.data.json import JSONify
from scs_core.sys.exception_report import ExceptionReport

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
        exit()

    if cmd.verbose:
        print(cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        io = IO()

        if cmd.verbose:
            print(io, file=sys.stderr)


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

    except Exception as ex:
        print(JSONify.dumps(ExceptionReport.construct(ex)), file=sys.stderr)

    finally:
        I2C.close()
