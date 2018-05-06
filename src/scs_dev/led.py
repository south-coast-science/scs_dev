#!/usr/bin/env python3

"""
Created on 20 Feb 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The led utility is used to control a two-colour (red / green) LED mounted on the South Coast Science free-to-air
SHT board.

On some Praxis device configurations, a free-to-air temperature and humidity board is mounted in the air intake of the
optical particle counter (OPC). Since the board is visible from outside the unit, it is useful to mount indicator
LEDs in this position.

LED options are as follows:

* R - Red
* A - Amber (Red + Green)
* G - Green
* 0 - Off

In practice, the led utility does a very simple job: it validates its parameters, then presents these on stdout in a
format that is compatible with the led_controller utility. Because the led_controller is typically running as an
independent process, it is appropriate to use a named pipe to send this communication.

If the led_controller is not running, the led utility will simply buffer commands in whatever communications pipe is
being used.

Note: the led utility is not currently supported on Raspberry Pi systems.

SYNOPSIS
led.py { -s { R | A | G | 0 } | -f { R | A | G | 0 } { R | A | G | 0 } } [-v] PIPE

EXAMPLES
./led.py -f R 0 > ~/SCS/pipes/led_control_pipe

DOCUMENT EXAMPLE
{"colour0": "R", "colour1": "G"}

SEE ALSO
scs_dev/led_controller

RESOURCES
https://unix.stackexchange.com/questions/139490/continuous-reading-from-named-pipe-cat-or-tail-f
"""

import os
import sys

from scs_core.data.json import JSONify

from scs_dev.cmd.cmd_led import CmdLED

from scs_dfe.display.led_state import LEDState


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    fifo = None

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdLED()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print("led: %s" % cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        if not os.path.exists(cmd.pipe):
            print("led: fifo does not exist: %s" % cmd.pipe, file=sys.stderr)
            exit(1)

        fifo = open(cmd.pipe, "w")


        # ------------------------------------------------------------------------------------------------------------
        # run...

        state = LEDState(cmd.solid, cmd.solid) if cmd.solid is not None else LEDState(cmd.flash[0], cmd.flash[1])

        print(JSONify.dumps(state), file=fifo)

        if cmd.verbose:
            print(JSONify.dumps(state), file=sys.stderr)

    finally:
        if fifo:
            fifo.close()
