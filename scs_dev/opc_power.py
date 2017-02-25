#!/usr/bin/env python3

"""
Created on 21 Jan 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

command line example:
./scs_dev/opc_power.py 1
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

    opc = None

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

        opc = OPCN2()

        if cmd.verbose:
            print(opc, file=sys.stderr)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        opc.power_on()

        if cmd.power:
            opc.operations_on()
        else:
            opc.operations_off()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt as ex:
        if cmd.verbose:
            print("opc_power: KeyboardInterrupt", file=sys.stderr)

    except Exception as ex:
        print(JSONify.dumps(ExceptionReport.construct(ex)), file=sys.stderr)

    finally:
        if opc:
            opc.power_off()

        I2C.close()
