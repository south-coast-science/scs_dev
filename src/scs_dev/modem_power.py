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
modem_power.py { 0 | 1 } [-v]

EXAMPLES
./modem_power.py 1
"""

import sys

from scs_core.sys.logging import Logging
from scs_core.sys.signalled_exit import SignalledExit

from scs_dev.cmd.cmd_power import CmdPower

from scs_dfe.interface.interface_conf import InterfaceConf

from scs_host.bus.i2c import I2C
from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    I2C.Utilities.open()

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdPower()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    # logging...
    Logging.config('modem_power', verbose=cmd.verbose)
    logger = Logging.getLogger()

    logger.info(cmd)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # Interface...
        interface_conf = InterfaceConf.load(Host)

        if interface_conf is None:
            logger.error("InterfaceConf not available.")
            exit(1)

        interface = interface_conf.interface()
        logger.info(interface)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        # signal handler...
        SignalledExit.construct()

        if cmd.all is not None:
            interface.power_modem(cmd.all)


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except ConnectionError as ex:
        logger.error(repr(ex))

    except (KeyboardInterrupt, SystemExit):
        pass

    finally:
        logger.info("finishing")

        I2C.Utilities.close()
