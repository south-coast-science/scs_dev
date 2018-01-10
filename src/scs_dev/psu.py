#!/usr/bin/env python3

"""
Created on 8 Aug 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

command line example:
./psu.py -p -v
"""

import sys

from scs_core.data.json import JSONify
from scs_core.sys.exception_report import ExceptionReport

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
            print(cmd, file=sys.stderr)


        # ------------------------------------------------------------------------------------------------------------
        # resource...

        psu_conf = PSUConf.load(Host)
        psu = psu_conf.psu(Host)

        if psu is None:
            print("psu: no PSU present", file=sys.stderr)
            exit(1)

        if cmd.verbose:
            print(psu, file=sys.stderr)
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

    except Exception as ex:
        print(JSONify.dumps(ExceptionReport.construct(ex)), file=sys.stderr)

    finally:
        if psu:
            psu.close()
