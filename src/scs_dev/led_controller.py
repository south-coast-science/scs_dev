#!/usr/bin/env python3

"""
Created on 30 Apr 2018

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The led_controller utility operates the a two-colour (red / green) LED mounted on the South Coast Science free-to-air
SHT board. LEDs can be made to flash or have steady state. The utility is intended to run as a systemd service, or as
an (un-managed) background process.

The led_controller waits for data on stdin, then updates the state of the LEDs accordingly. Updates are in the form
of a JSON array containing two single-character strings - the first represents 80% of the duty cycle, the second 20%.
If a steady state is required, the two values should be the same.

When the led_controller starts, the LEDs remain in their previous state. When the led_controller terminates,
the LEDs remain in their last state.

SYNOPSIS
led_controller -v

EXAMPLES
( tail -f ~/SCS/pipes/led_control_pipe & ) | ./led_controller.py -v &

DOCUMENT EXAMPLE
{"colour0": "R", "colour1": "G"}

SEE ALSO
scs_dev/led

RESOURCES
https://unix.stackexchange.com/questions/139490/continuous-reading-from-named-pipe-cat-or-tail-f
"""

import json
import sys

from collections import OrderedDict

from scs_core.data.json import JSONify

from scs_dev.cmd.cmd_verbose import CmdVerbose

from scs_dfe.display.led_controller import LEDController
from scs_dfe.display.led_state import LEDState

from scs_host.bus.i2c import I2C
from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    supervisor = None

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdVerbose()

    if cmd.verbose:
        print("led_controller: %s" % cmd, file=sys.stderr)
        sys.stderr.flush()

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        I2C.open(Host.I2C_SENSORS)

        supervisor = LEDController()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        supervisor.start()

        for line in sys.stdin:
            try:
                jdict = json.loads(line, object_pairs_hook=OrderedDict)
            except ValueError:
                continue

            state = LEDState.construct_from_jdict(jdict)

            if state is None:
                continue

            if cmd.verbose:
                print("led_controller: %s" % JSONify.dumps(state), file=sys.stderr)
                sys.stderr.flush()

            if not state.is_valid():
                continue

            supervisor.set_state(state)


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        if cmd.verbose:
            print("led_controller: KeyboardInterrupt", file=sys.stderr)

    finally:
        I2C.close()
