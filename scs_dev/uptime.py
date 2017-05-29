#!/usr/bin/env python3

"""
Created on 29 May 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

command line example:
./uptime.py
"""

import subprocess

from scs_core.data.json import JSONify
from scs_core.data.localized_datetime import LocalizedDatetime

from scs_core.sys.uptime_datum import UptimeDatum


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    now = LocalizedDatetime.now()

    raw = subprocess.check_output('uptime')
    report = raw.decode()

    datum = UptimeDatum.construct_from_report(now, report)

    print(JSONify.dumps(datum))
