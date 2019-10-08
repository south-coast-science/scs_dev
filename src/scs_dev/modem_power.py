#!/usr/bin/env python3

"""
Created on 28 Feb 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The modem_power utility is used to apply or remove power to the South Coast Science 2G modem board for BeagleBone.

Note: in some operating system configurations, the modem board is under control of the Debian modem manager. In these
cases, the modem manager may override the operation of this utility. The modem_power utility is not available on
Raspberry Pi systems.

SYNOPSIS
modem_power.py { 1 | 0 } [-v]

EXAMPLES
./modem_power.py 1
"""

import sys

from scs_core.sys.signalled_exit import SignalledExit

from scs_dev.cmd.cmd_power import CmdPower

from scs_dfe.interface.interface_conf import InterfaceConf

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
        print("modem_power: %s" % cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # Interface...
        interface_conf = InterfaceConf.load(Host)

        if interface_conf is None:
            print("modem_power: InterfaceConf not available.", file=sys.stderr)
            exit(1)

        interface = interface_conf.interface()

        if cmd.verbose:
            print("modem_power: %s" % interface, file=sys.stderr)
            sys.stderr.flush()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        # signal handler...
        SignalledExit.construct("modem_power", cmd.verbose)

        if cmd.all is not None:
            interface.power_modem(cmd.all)          # TODO: implement 2G modem power control


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except (BrokenPipeError, ConnectionResetError) as ex:
        print("modem_power: %s" % ex, file=sys.stderr)

    except SystemExit:
        pass

    finally:
        if cmd and cmd.verbose:
            print("modem_power: finishing", file=sys.stderr)

        I2C.close()
