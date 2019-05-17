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
scs_dev/opc_power
scs_dev/opc_version
scs_mfr/opc_cleaning_interval
scs_mfr/opc_conf
scs_dev/particulates_sampler
"""

import sys

from scs_dev.cmd.cmd_opc_cleaner import CmdOPCCleaner

from scs_dfe.particulate.opc_conf import OPCConf

from scs_host.bus.i2c import I2C
from scs_host.sys.host import Host


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
        conf = OPCConf.load_from_file(cmd.file) if cmd.file else OPCConf.load(Host)

        if conf is None:
            print("opc_cleaner: OPCConf not available.", file=sys.stderr)
            exit(1)

        # OPC...
        opc = conf.opc(Host)

        if cmd.verbose:
            print("opc_cleaner: %s" % opc, file=sys.stderr)
            sys.stderr.flush()

        # I2C...
        i2c_bus = Host.I2C_SENSORS if opc.uses_spi() else opc.bus

        I2C.open(i2c_bus)


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
