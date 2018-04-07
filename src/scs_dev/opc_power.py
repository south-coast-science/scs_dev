#!/usr/bin/env python3

"""
Created on 26 Mar 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The opc_power utility is used to apply or remove power to the Alphasense optical particle counter (OPC). The utility
may be used to save power, or to cycle an OPC whose laser safety system has tripped.

Note: Power to the OPC is also under the control of the OPC monitor process launched by the particulates_sampler
utility. If running, the OPC monitor process will override the action of this script.

Note: Raspberry Pi systems do not have the ability to control the OPC power. For these systems, the OPC is simply
commanded to stop or start operations.

SYNOPSIS
opc_power.py { 1 | 0 } [-v]

EXAMPLES
./opc_power.py 1

SEE ALSO
scs_dev/dfe_power
"""

import sys

from scs_dev.cmd.cmd_power import CmdPower

from scs_dfe.particulate.opc_n2 import OPCN2

from scs_host.bus.i2c import I2C
from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdPower()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(1)

    if cmd.verbose:
        print(cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        I2C.open(Host.I2C_SENSORS)

        opc = OPCN2(Host.opc_spi_bus(), Host.opc_spi_device())


        # ------------------------------------------------------------------------------------------------------------
        # run...

        if cmd.power:
            # OPC...
            opc.power_on()
            opc.operations_on()

        else:
            # OPC...
            opc.operations_off()
            opc.power_off()

        if cmd.verbose:
            print(opc, file=sys.stderr)
            sys.stderr.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    finally:
        I2C.close()
