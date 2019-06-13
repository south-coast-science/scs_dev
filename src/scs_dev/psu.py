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

BUGS
The psu utility is typically locked by the status_sampler utility, and is therefore not available to other processes.
"""

import sys

from scs_dev.cmd.cmd_psu import CmdPSU

from scs_host.sys.host import Host

from scs_psu.psu.psu_conf import PSUConf


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    cmd = None
    psu = None

    try:
        # ------------------------------------------------------------------------------------------------------------
        # cmd...

        cmd = CmdPSU()

        if not cmd.is_valid():
            cmd.print_help(sys.stderr)
            exit(2)

        if cmd.verbose:
            print("psu: %s" % cmd, file=sys.stderr)


        # ------------------------------------------------------------------------------------------------------------
        # resource...

        psu_conf = PSUConf.load(Host)
        psu = psu_conf.psu(Host)

        if psu is None:
            print("psu: no PSU present", file=sys.stderr)
            exit(1)

        if cmd.verbose:
            print("psu: %s" % psu, file=sys.stderr)
            sys.stderr.flush()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        psu.open()

        if cmd.has_psu_command():
            # use cmd args...
            response = psu.communicate(cmd.psu_command)
            print(response)

        else:
            # use stdin...
            if cmd.interactive:
                print('> ', file=sys.stderr, end='')
                sys.stderr.flush()

            for line in sys.stdin:
                response = psu.communicate(line.strip())
                print(response)
                sys.stdout.flush()

                if cmd.interactive:
                    print('> ', file=sys.stderr, end='')
                    sys.stderr.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        if cmd.interactive:
            print("", file=sys.stderr)

        if cmd.verbose:
            print("psu: KeyboardInterrupt", file=sys.stderr)

    finally:
        if psu:
            psu.close()
