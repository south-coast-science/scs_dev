#!/usr/bin/env python3

"""
Created on 23 Jun 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

(cat /home/pi/SCS/pipes/display_pipe &) | ./display.py -v
"""

import sys

from scs_core.data.localized_datetime import LocalizedDatetime
from scs_core.sync.interval_timer import IntervalTimer


# --------------------------------------------------------------------------------------------------------------------

fifo = None

try:
    fifo = open('/home/pi/SCS/pipes/display_pipe', 'w')

    timer = IntervalTimer(10)

    while timer.true():
        now = LocalizedDatetime.now()
        message = "test: %s" % now.as_iso8601()

        print(message, file=fifo)
        fifo.flush()

        print(message, file=sys.stderr)
        sys.stderr.flush()


except KeyboardInterrupt:
    print("KeyboardInterrupt", file=sys.stderr)

finally:
    print("exiting", file=sys.stderr)

    if fifo:
        fifo.close()
