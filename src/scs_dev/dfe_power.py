#!/usr/bin/env python3

"""
Created on 28 Feb 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The dfe_power utility is used to simultaneously switch on and off the power to GPS, OPC, NDIR and LED peripherals.

Warning: the command is fully-functional only with the South Coast Science digital front-end (DFE) board for BeagleBone.
For other DFE boards - such as that for RaspBerry Pi - the command is only able to command a operation start / stop to
the OPC.

EXAMPLES
./dfe_power.py -v 0

SEE ALSO
scs_dev/opc_power
"""

import sys

from scs_dev.cmd.cmd_power import CmdPower

from scs_dfe.board.io import IO
from scs_dfe.particulate.opc_n2 import OPCN2

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

        opc = OPCN2(Host.opc_spi_bus(), Host.opc_spi_device())


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
            opc.operations_off()         # needed because some DFEs do not have OPC power control

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
