#!/usr/bin/env python3

"""
Created on 28 Feb 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

command line example:
./scs_dev/dfe_power.py -v 0
"""

import sys

from scs_core.data.json import JSONify
from scs_core.sys.exception_report import ExceptionReport

from scs_dev.cmd.cmd_power import CmdPower

from scs_dfe.board.io import IO

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
        # resource...

        io = IO()

        if cmd.verbose:
            print(io, file=sys.stderr)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        if cmd.power:
            # DFE...
            io.gps_power = IO.LOW
            io.opc_power = IO.LOW
            io.ndir_power = IO.LOW

            io.led_red = IO.HIGH
            io.led_green = IO.HIGH

        else:
            # DFE...
            io.gps_power = IO.HIGH
            io.opc_power = IO.HIGH
            io.ndir_power = IO.HIGH

            io.led_red = IO.LOW
            io.led_green = IO.LOW


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except Exception as ex:
        print(JSONify.dumps(ExceptionReport.construct(ex)), file=sys.stderr)

    finally:
        I2C.close()
