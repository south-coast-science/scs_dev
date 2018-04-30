#!/usr/bin/env python3

"""
Created on 20 Feb 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The led utility is used to control a two-colour (red / green) LED mounted on the South Coast Science free-to-air
SHT board.

On some Praxis device configurations, a free-to-air temperature and humidity board is mounted in the air intake of the
optical particle counter (OPC). Since the board is visible from outside the unit, it is useful to mount an indicator
LED in this position.

LED options are as follows:

* R - red
* G - green
* O - orange
* 0 - off

The led utility writes the state of the LED to stdout.

When the system powers up, the LED defaults to orange.

Note: the led utility is not available on Raspberry Pi systems.

SYNOPSIS
led.py [-s { R | G | O | 0 }] [-v]

EXAMPLES
./led.py -s R

"""

import sys

from scs_core.data.json import JSONify

from scs_dev.cmd.cmd_led import CmdLED

from scs_dfe.display.led import LED

from scs_host.bus.i2c import I2C
from scs_host.sys.host import Host


# TODO: add flashing mode, and add to cmd list for remote device identification

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

        print("%s" % led.colour)


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    finally:
        I2C.close()
