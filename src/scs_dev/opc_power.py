#!/usr/bin/env python3

"""
Created on 26 Mar 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

command line example:
./opc_power.py -v 0
"""

import sys

from scs_core.data.json import JSONify
from scs_core.sys.exception_report import ExceptionReport

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


        opc = OPCN2(Host.OPC_SPI_BUS, Host.OPC_SPI_DEVICE)


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

    except Exception as ex:
        print(JSONify.dumps(ExceptionReport.construct(ex)), file=sys.stderr)

    finally:
        I2C.close()
