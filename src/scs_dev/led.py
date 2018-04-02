#!/usr/bin/env python3

"""
Created on 20 Feb 2017

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
scs_dev/



command line example:
./led.py -s G
"""

import sys

from scs_dev.cmd.cmd_led import CmdLED

from scs_dfe.display.led import LED

from scs_host.bus.i2c import I2C
from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdLED()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print(cmd, file=sys.stderr)
        sys.stderr.flush()

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        I2C.open(Host.I2C_SENSORS)

        led = LED()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        if cmd.set():
            led.colour = cmd.colour

        print(led.colour)


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    finally:
        I2C.close()
