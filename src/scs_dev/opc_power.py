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
opc_power.py [-f FILE] { 1 | 0 } [-v]

EXAMPLES
./opc_power.py 1

SEE ALSO
scs_dev/dfe_power
scs_dev/opc_version
scs_dev/particulates_sampler
scs_mfr/opc_conf
"""

import sys

from scs_dev.cmd.cmd_opc_power import CmdOPCPower

from scs_dfe.board.dfe_conf import DFEConf
from scs_dfe.particulate.opc_conf import OPCConf

from scs_host.bus.i2c import I2C
from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdOPCPower()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(1)

    if cmd.verbose:
        print("opc_power: %s" % cmd, file=sys.stderr)
        sys.stderr.flush()

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # DFEConf...
        dfe_conf = DFEConf.load(Host)

        if dfe_conf is None:
            print("dfe_power: DFEConf not available.", file=sys.stderr)
            exit(1)

        if cmd.verbose and dfe_conf:
            print("dfe_power: %s" % dfe_conf, file=sys.stderr)

        # OPCConf...
        opc_conf = OPCConf.load_from_file(cmd.file) if cmd.file else OPCConf.load(Host)

        if opc_conf is None:
            print("opc_power: OPCConf not available.", file=sys.stderr)
            exit(1)

        # OPC...
        opc = opc_conf.opc(Host, dfe_conf.load_switch_active_high)

        # I2C...
        i2c_bus = Host.I2C_SENSORS if opc.uses_spi() else opc.bus

        I2C.open(i2c_bus)


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
            print("opc_power: %s" % opc, file=sys.stderr)
            sys.stderr.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    finally:
        I2C.close()
