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

In practice, the led utility does a very simple job: it validates its parameters, then presents these on stdout or
the named Unix domain socket in a format that is compatible with the led_controller utility.

If the Unix domain socket has no listener, the led utility discards messages.

Note: the led utility is not currently supported on Raspberry Pi systems.

SYNOPSIS
led.py { -s { R | A | G | 0 } | -f { R | A | G | 0 } { R | A | G | 0 } } [-u UDS] [-v]

EXAMPLES
./led.py -v -f R 0 -u /home/scs/SCS/pipes/scs_led_control.uds

DOCUMENT EXAMPLE
{"colour0": "R", "colour1": "G"}

SEE ALSO
scs_dev/led_controller
"""

import sys

from scs_core.data.json import JSONify

from scs_core.sys.signalled_exit import SignalledExit

from scs_dev.cmd.cmd_led import CmdLED

from scs_dfe.display.led_state import LEDState

from scs_host.comms.domain_socket import DomainSocket


# --------------------------------------------------------------------------------------------------------------------
# output writer...

class LEDWriter(object):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, uds_name):
        """
        Constructor
        """
        self.__uds = DomainSocket(uds_name) if uds_name else None


    # ----------------------------------------------------------------------------------------------------------------

    def connect(self):
        if self.__uds:
            self.__uds.connect(False)


    def close(self):
        if self.__uds:
            self.__uds.close()


    def write(self, message):
        if self.__uds:
            self.__uds.write(message, False)

        else:
            print(message)


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "LEDWriter:{uds:%s}" % self.__uds


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    writer = None

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

        # signal handler...
        SignalledExit.construct("led", cmd.verbose)

        writer = LEDWriter(cmd.uds)

        if cmd.verbose:
            print("led: %s" % writer, file=sys.stderr)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        state = LEDState(cmd.solid, cmd.solid) if cmd.solid is not None else LEDState(cmd.flash[0], cmd.flash[1])

        writer.connect()

        try:
            writer.write(JSONify.dumps(state))

            if cmd.verbose:
                print(JSONify.dumps(state), file=sys.stderr)

        except OSError:
            if cmd.verbose:
                print("led: unable to write to %s" % cmd.uds, file=sys.stderr)


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except BrokenPipeError:
        pass

    finally:
        if writer:
            writer.close()

        sys.stderr.close()
