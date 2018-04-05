#!/usr/bin/env python3

"""
Created on 13 Jun 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The ps utility is used to run the Unix ps (process snapshot) command. The utility present the output of the ps command
as a JSON document, making it suitable for analysis by a remote device management system.

The ps utility is normally included in the commands accepted by the control_receiver utility.

SYNOPSIS
ps.py

EXAMPLES
./ps.py

DOCUMENT EXAMPLE - OUTPUT
{"ppid": 1069, "pid": 1071, "uid": 1000, "tty": "?", "pcpu": 0.9, "pmem": 0.0, "cpu": "00-00:00:03.000",
"elapsed": "00-02:50:12.000", "cmd": "python3 /home/pi/SCS/scs_dev/src/scs_dev/osio_topic_publisher.py -v -cG"}

SEE ALSO
scs_dev/control_receiver
scs_dev/uptime
"""

import subprocess

from scs_core.data.json import JSONify

from scs_core.sys.ps_datum import PsDatum


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    p1 = subprocess.Popen(['ps', '-Ao', 'ppid,pid,uid,tty,pmem,pcpu,cputime,etime,args'],
                          stdout=subprocess.PIPE)

    p2 = subprocess.Popen(['grep', 'SCS'], stdin=p1.stdout, stdout=subprocess.PIPE)
    p1.stdout.close()       # Allow p1 to receive a SIGPIPE if p2 exits.

    raw = p2.communicate()[0]
    report = raw.decode()

    for line in [line.strip() for line in report.split('\n')]:
        if len(line) == 0:
            continue

        datum = PsDatum.construct_from_report(line)

        if datum is None or 'ps.py' in datum.cmd or 'grep' in datum.cmd:
            continue

        print(JSONify.dumps(datum))
