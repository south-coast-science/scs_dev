#!/usr/bin/env python3

"""
Created on 28 Feb 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The interface_power utility is used to simultaneously switch on and off the power to GPS, OPC, NDIR and LED peripherals.

Note: the command is fully-functional only with the South Coast Science digital front-end (DFE) board for BeagleBone.
For other DFE boards - such as that for Raspberry Pi - the utility is only able to command a operation start / stop to
the NDIR and OPC.

SYNOPSIS
interface_power.py { 1 | 0 } [-v]

EXAMPLES
./interface_power.py 0

SEE ALSO
scs_dev/opc_power
"""

import sys

from scs_core.sys.signalled_exit import SignalledExit

from scs_dev.cmd.cmd_power import CmdPower

from scs_dfe.interface.components.io import IO
from scs_dfe.interface.interface_conf import InterfaceConf

from scs_dfe.particulate.opc_conf import OPCConf

from scs_host.bus.i2c import I2C
from scs_host.sys.host import Host

try:
    from scs_ndir.gas.ndir_conf import NDIRConf
except ImportError:
    from scs_core.gas.ndir_conf import NDIRConf


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
        print("interface_power: %s" % cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # signal handler...
        SignalledExit.construct("interface_power", cmd.verbose)

        # Interface...
        interface_conf = InterfaceConf.load(Host)

        if interface_conf is None:
            print("interface_power: InterfaceConf not available.", file=sys.stderr)
            exit(1)

        interface = interface_conf.interface()

        io = IO(interface.load_switch_active_high)

        if cmd.verbose:
            print("interface_power: %s" % io, file=sys.stderr)
            sys.stderr.flush()

        # OPC...
        opc_conf = OPCConf.load(Host)
        opc = None if opc_conf is None else opc_conf.opc(Host, interface.load_switch_active_high)

        if cmd.verbose and opc_conf:
            print("interface_power: %s" % opc_conf, file=sys.stderr)

        # NDIR...
        ndir_conf = NDIRConf.load(Host)
        ndir = None if ndir_conf is None else ndir_conf.ndir(Host)

        if cmd.verbose and ndir_conf:
            print("interface_power: %s" % ndir_conf, file=sys.stderr)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        if cmd.power:
            # Interface...
            io.gps_power = True
            io.opc_power = True
            io.ndir_power = True

            io.led_red = True
            io.led_green = True

        else:
            # OPC...
            if opc:
                opc.operations_off()         # needed because some DFEs do not have power control

            # NDIR...
            if ndir:
                ndir.lamp_run(False)         # needed because some DFEs do not have power control

            # Interface...
            io.gps_power = False
            io.opc_power = False
            io.ndir_power = False

            io.led_red = False
            io.led_green = False


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except (BrokenPipeError, ConnectionResetError):
        pass

    finally:
        I2C.close()
