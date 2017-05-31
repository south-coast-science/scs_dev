#!/usr/bin/env python3

"""
Created on 18 Aug 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

command line example:
./status_sampler.py -n 10 | ./socket_sender.py bruno.local -e
"""

import sys

from scs_core.data.json import JSONify
from scs_core.sys.exception_report import ExceptionReport

from scs_dev.cmd.cmd_socket_sender import CmdSocketSender

from scs_host.comms.network_socket import NetworkSocket


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    sender = None

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSocketSender()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit()

    if cmd.verbose:
        print(cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        sender = NetworkSocket(cmd.hostname, cmd.port)

        if cmd.verbose:
            print(sender, file=sys.stderr)
            sys.stderr.flush()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        sender.connect(True)

        for line in sys.stdin:
            sender.write(line, True)

            if cmd.echo:
                print(line.strip())
                sys.stdout.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt as ex:
        if cmd.verbose:
            print("socket_sender: KeyboardInterrupt", file=sys.stderr)

    except Exception as ex:
        print(JSONify.dumps(ExceptionReport.construct(ex)), file=sys.stderr)

    finally:
        if sender:
            sender.close()
