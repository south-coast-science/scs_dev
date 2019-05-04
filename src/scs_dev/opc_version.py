#!/usr/bin/env python3

"""
Created on 4 Sep 2018

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The opc_version utility requests the firmware version from the Alphasense optical particle counter (OPC).
The reported string is written to stdout.

The opc_version utility exits with 1 if no version string could be read, and exits with 0 if a string was read. The
command can therefore be used to test for the presence / operability of an OPC.

SYNOPSIS
opc_version.py [-v]

EXAMPLES
./opc_version.py -v

FILES
~/SCS/conf/opc_conf.json

DOCUMENT EXAMPLE - OUTPUT
"OPC-N2 FirmwareVer=OPC-018.2..............................BD"

SEE ALSO
scs_dev/opc_cleaner
scs_dev/opc_power
scs_dev/particulates_sampler
scs_mfr/opc_conf
"""

import sys

from scs_dev.cmd.cmd_verbose import CmdVerbose

from scs_dfe.particulate.opc_conf import OPCConf

from scs_host.bus.i2c import I2C
from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdVerbose()

    if cmd.verbose:
        print("opc_version: %s" % cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        I2C.open(Host.I2C_SENSORS)

        # OPCConf...
        opc_conf = OPCConf.load(Host)

        if opc_conf is None:
            print("opc_version: OPCConf not available.", file=sys.stderr)
            exit(1)

        # OPC...
        opc = opc_conf.opc(Host)

        if cmd.verbose:
            print("opc_version: %s" % opc, file=sys.stderr)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        opc.power_on()

        version = opc.firmware()

        if not version:
            print("opc_version: OPC not available", file=sys.stderr)
            exit(1)

        print("opc_version: %s" % version, file=sys.stderr)

        opc.power_off()

    # ----------------------------------------------------------------------------------------------------------------
    # end...

    finally:
        I2C.close()
