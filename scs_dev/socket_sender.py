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

from scs_dfe.network.socket_sender import SocketSender


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    sckt = None
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

        sckt = SocketSender(cmd.hostname, cmd.port, cmd.verbose)

        if cmd.verbose:
            print(sckt, file=sys.stderr)

        sender = sckt.sender()
        sender.__next__()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        for line in sys.stdin:
            sender.send(line)

            if cmd.echo:
                print(line, end="", file=sys.stderr)
                sys.stderr.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt as ex:
        if cmd.verbose:
            print("socket_sender: KeyboardInterrupt", file=sys.stderr)

    except Exception as ex:
        print(JSONify.dumps(ExceptionReport.construct(ex)), file=sys.stderr)

    finally:
        if sckt is not None:
            try:
                sender.close()
            except Exception as ex:
                print(JSONify.dumps(ExceptionReport.construct(ex)), file=sys.stderr)

            try:
                sckt.close()
            except Exception as ex:
                print(JSONify.dumps(ExceptionReport.construct(ex)), file=sys.stderr)
