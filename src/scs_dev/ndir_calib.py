#!/usr/bin/env python3

"""
Created on 17 Feb 2018

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The XX utility is used to .

EXAMPLES
xx

FILES
~/SCS/aws/

DOCUMENT EXAMPLE
xx

SEE ALSO
scs_ndir/



command line example:
./ndir_calib.py -s min-deferral 740
"""

import sys

from scs_core.data.json import JSONify
from scs_core.data.path_dict import PathDict

from scs_dev.cmd.cmd_ndir_calib import CmdNDIRCalib

from scs_host.bus.i2c import I2C
from scs_host.sys.host import Host

from scs_ndir.exception.ndir_exception import NDIRException

from scs_ndir.gas.ndir import NDIR
from scs_ndir.gas.ndir_calib import NDIRCalib


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdNDIRCalib()

    if cmd.verbose:
        print(cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        I2C.open(Host.I2C_SENSORS)

        ndir = NDIR(Host.ndir_spi_bus(), Host.ndir_spi_device())
        ndir.power_on()

        # ------------------------------------------------------------------------------------------------------------
        # run...

        if cmd.default:
            calib = NDIRCalib.default()

            # save...
            ndir.store_calib(calib)

        elif cmd.restart:
            ndir.reload_calib()

        elif cmd.set():
            # retrieve...
            calib = ndir.retrieve_calib()
            dictionary = PathDict.construct_from_jstr(JSONify.dumps(calib))

            # validate...
            if not dictionary.has_path(cmd.path):
                print("ndir_calib: field name not known: %s" % cmd.path, file=sys.stderr)
                exit(2)

            # set...
            dictionary.append(cmd.path, cmd.value)
            calib = NDIRCalib.construct_from_jdict(dictionary.as_json())

            # validate...
            dictionary = PathDict.construct_from_jstr(JSONify.dumps(calib))

            if dictionary.node(cmd.path) is None:
                print("ndir_calib: field value not acceptable: %s" % cmd.value, file=sys.stderr)
                exit(2)

            # save...
            ndir.store_calib(calib)

        # confirm...
        calib = ndir.retrieve_calib()

        # report...
        print(JSONify.dumps(calib))


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except NDIRException as ex:
        jstr = JSONify.dumps(ex)
        print(jstr, file=sys.stderr)

    except KeyboardInterrupt:
        print("")

    finally:
        I2C.close()
