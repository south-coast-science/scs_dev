#!/usr/bin/env python3

"""
Created on 3 May 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The opc_power utility is used to ...

SYNOPSIS
opc_cleaner.py [-f FILE]

EXAMPLES
./opc_cleaner.py

SEE ALSO
scs_dev/particulates_sampler

scs_mfr/opc_cleaning_interval
scs_mfr/opc_conf
scs_mfr/opc_version
"""

import sys

from scs_dev.cmd.cmd_opc_cleaner import CmdOPCCleaner

from scs_dfe.interface.interface_conf import InterfaceConf
from scs_dfe.particulate.opc_conf import OPCConf

from scs_host.bus.i2c import I2C
from scs_host.sys.host import Host


# TODO: handle OPC power-down issue

# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdOPCCleaner()

    if cmd.verbose:
        print("opc_cleaner: %s" % cmd, file=sys.stderr)
        sys.stderr.flush()

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # OPCConf...
        opc_conf = OPCConf.load_from_file(cmd.file) if cmd.file else OPCConf.load(Host)

        if opc_conf is None:
            print("opc_cleaner: OPCConf not available.", file=sys.stderr)
            exit(1)

        # I2C...
        i2c_bus = Host.I2C_SENSORS if opc_conf.uses_spi() else opc_conf.bus
        I2C.open(i2c_bus)

        # Interface...
        interface_conf = InterfaceConf.load(Host)

        if interface_conf is None:
            print("opc_cleaner: InterfaceConf not available.", file=sys.stderr)
            exit(1)

        interface = interface_conf.interface()

        if interface is None:
            print("opc_cleaner: Interface not available.", file=sys.stderr)
            exit(1)

        if cmd.verbose and interface:
            print("opc_cleaner: %s" % interface, file=sys.stderr)

        # OPC...
        opc = opc_conf.opc(interface, Host)

        if cmd.verbose:
            print("opc_cleaner: %s" % opc, file=sys.stderr)
            sys.stderr.flush()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        if cmd.power:
            opc.power_on()
            opc.operations_on()

        opc.clean()

        if cmd.power:
            opc.operations_off()
            opc.power_off()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    finally:
        I2C.close()
