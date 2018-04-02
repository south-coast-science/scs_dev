#!/usr/bin/env python3

"""
Created on 29 May 2017

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
./uptime.py
"""

import subprocess
import sys

from scs_core.data.json import JSONify
from scs_core.data.localized_datetime import LocalizedDatetime

from scs_core.sys.exception_report import ExceptionReport
from scs_core.sys.uptime_datum import UptimeDatum

from scs_dev.cmd.cmd_sampler import CmdSampler


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSampler()

    if cmd.verbose:
        print(cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # run...

        now = LocalizedDatetime.now()

        raw = subprocess.check_output('uptime')
        report = raw.decode()

        datum = UptimeDatum.construct_from_report(now, report)

        print(JSONify.dumps(datum))


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        if cmd.verbose:
            print("uptime: KeyboardInterrupt", file=sys.stderr)

    except Exception as ex:
        print(JSONify.dumps(ExceptionReport.construct(ex)), file=sys.stderr)

