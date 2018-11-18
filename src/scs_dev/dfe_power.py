#!/usr/bin/env python3

"""
Created on 28 Feb 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The dfe_power utility is used to simultaneously switch on and off the power to GPS, OPC, NDIR and LED peripherals.

Note: the command is fully-functional only with the South Coast Science digital front-end (DFE) board for BeagleBone.
For other DFE boards - such as that for Raspberry Pi - the utility is only able to command a operation start / stop to
the OPC.

SYNOPSIS
dfe_power.py { 1 | 0 } [-v]

EXAMPLES
./dfe_power.py 0

SEE ALSO
scs_dev/opc_power
"""

import sys

from scs_dev.cmd.cmd_power import CmdPower

from scs_dfe.board.io import IO
# from scs_dfe.particulate.opc_n2.opc_n2 import OPCN2

from scs_host.bus.i2c import I2C
from scs_host.sys.host import Host


# TODO: shut down OPC and NDIR if confs are available

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
        print("dfe_power: %s" % cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        io = IO()

        if cmd.verbose:
            print("dfe_power: %s" % io, file=sys.stderr)
            sys.stderr.flush()

        # opc = OPCN2(Host.opc_spi_bus(), Host.opc_spi_device())


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
            # OPC...
            # opc.operations_off()         # needed because some DFEs do not have OPC power control

            # DFE...
            io.gps_power = IO.HIGH
            io.opc_power = IO.HIGH
            io.ndir_power = IO.HIGH

            io.led_red = IO.LOW
            io.led_green = IO.LOW


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    finally:
        I2C.close()
