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

from scs_dev.cmd.cmd_opc_power import CmdOPCPower

from scs_dfe.particulate.opc_n2 import OPCN2


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    opc = None

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdOPCPower()

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
