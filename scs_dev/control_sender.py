#!/usr/bin/env python3

"""
Created on 17 Apr 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

command line example:
./scs_dev/control_sender.py scs-ap1-6 00000000cda1f8b9 shutdown now -v
"""

import sys

from scs_core.control.control_datum import ControlDatum
from scs_core.data.json import JSONify
from scs_core.data.localized_datetime import LocalizedDatetime
from scs_core.sys.exception_report import ExceptionReport

from scs_dev.cmd.cmd_control_sender import CmdControlSender


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdControlSender()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit()

    if cmd.verbose:
        print(cmd, file=sys.stderr)

    try:

        # ------------------------------------------------------------------------------------------------------------
        # run...

        now = LocalizedDatetime.now()

        datum = ControlDatum.construct(cmd.tag, now, cmd.command, cmd.params, cmd.serial_number)

        print(JSONify.dumps(datum))
        sys.stdout.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except Exception as ex:
        print(JSONify.dumps(ExceptionReport.construct(ex)), file=sys.stderr)
