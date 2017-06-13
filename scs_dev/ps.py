#!/usr/bin/env python3

"""
Created on 13 Jun 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

command line example:
./ps.py
"""

import subprocess
import sys

from scs_core.data.json import JSONify

from scs_core.sys.exception_report import ExceptionReport
from scs_core.sys.ps_datum import PsDatum


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    try:
        p1 = subprocess.Popen(['ps', '-Ao', 'ppid,pid,uid,tty,pmem,pcpu,cputime,etime,args'],
                              stdout=subprocess.PIPE)

        p2 = subprocess.Popen(['grep', 'SCS'], stdin=p1.stdout, stdout=subprocess.PIPE)
        p1.stdout.close()       # Allow p1 to receive a SIGPIPE if p2 exits.

        raw = p2.communicate()[0]
        report = raw.decode()

        processes = []

        for line in [line.strip() for line in report.split('\n')]:
            if len(line) == 0:
                continue

            datum = PsDatum.construct_from_report(line)

            if datum is None or 'ps.py' in datum.cmd or 'grep python' in datum.cmd:
                continue

            processes.append(datum)

        print(JSONify.dumps(processes))

    except Exception as ex:
        print(JSONify.dumps(ExceptionReport.construct(ex)), file=sys.stderr)
