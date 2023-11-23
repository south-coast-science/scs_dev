#!/usr/bin/env python3

"""
Created on 8 Aug 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The psu utility is used to communicate with the South Coast Science power supply (SerialPSU) boards for BeagleBone via a
serial port connection.

The utility can be used in either of two modes:

* Interactive - the user is given a command prompt. A series of commands can be issued.
* Command - a single PSU command is supplied as a command line parameter

Note: the psu utility is not available on Raspberry Pi systems.

SYNOPSIS
psu.py { -i | CMD [PARAMS] } [-v]

EXAMPLES
./psu.py -i

FILES
~/SCS/conf/psu_conf.json

SEE ALSO
scs_mfr/psu_conf
"""

import os
import sys

from scs_core.sys.logging import Logging
from scs_core.sys.signalled_exit import SignalledExit

from scs_dev.cmd.cmd_psu import CmdPSU

from scs_dfe.interface.interface_conf import InterfaceConf

from scs_host.bus.i2c import I2C
from scs_host.comms.stdio import StdIO
from scs_host.lock.lock_timeout import LockTimeout
from scs_host.sys.host import Host

from scs_psu.psu.psu_conf import PSUConf


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    history_filename = os.path.join(Host.scs_path(), PSUConf.conf_dir(), 'psu_history.history')

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdPSU()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    # logging...
    Logging.config('psu_monitor', verbose=cmd.verbose)
    logger = Logging.getLogger()

    logger.info(cmd)

    try:
        I2C.Utilities.open()

        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # Interface...
        interface_conf = InterfaceConf.load(Host)
        interface = None if interface_conf is None else interface_conf.interface()
        interface_model = None if interface_conf is None else interface_conf.model

        # PSU...
        psu_conf = PSUConf.load(Host)
        psu = psu_conf.psu(Host, interface_model)

        if psu is None:
            logger.error("no PSU present.")
            exit(1)

        logger.info(psu)

        StdIO.set(history_filename=history_filename)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        # signal handler...
        SignalledExit.construct()

        if cmd.has_psu_command():
            # use cmd args...
            response = psu.communicate(cmd.psu_command)
            print(response)

        else:
            # use stdin...
            while True:
                command = StdIO.prompt('psu')

                if not command:
                    continue

                response = psu.communicate(command)
                print(response)
                sys.stdout.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except (ConnectionError, LockTimeout) as ex:
        logger.error(repr(ex))

    except (KeyboardInterrupt, SystemExit):
        pass

    finally:
        logger.info("finishing")

        if cmd.interactive:
            StdIO.save_history(history_filename)

        I2C.Utilities.close()
