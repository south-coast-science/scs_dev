#!/usr/bin/env python3

"""
Created on 29 May 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The uptime utility is used to run the Unix uptime command. The utility present the output of the uptime command
as a JSON document, making it suitable for analysis by a remote device management system.

The uptime report is included in the status_sampler report.

SYNOPSIS
uptime.py

EXAMPLES
./uptime.py

DOCUMENT EXAMPLE - OUTPUT
{"time": "2018-04-05T14:27:00.877+00:00", "period": "00-00:18:00.000", "users": 3,
"load": {"av1": 0.14, "av5": 0.09, "av15": 0.09}}

SEE ALSO
scs_dev/ps
"""

import subprocess

from scs_core.data.json import JSONify
from scs_core.data.localized_datetime import LocalizedDatetime

from scs_core.sys.uptime_datum import UptimeDatum


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # run...

    now = LocalizedDatetime.now()

    raw = subprocess.check_output('uptime')
    report = raw.decode()

    datum = UptimeDatum.construct_from_report(now, report)

    print(JSONify.dumps(datum))
