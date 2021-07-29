#!/usr/bin/env python3

"""
Created on 22 Jul 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

./display.py -v -u /home/pi/SCS/pipes/display.uds
"""

import sys

from scs_core.data.datetime import LocalizedDatetime
from scs_core.sync.interval_timer import IntervalTimer

from scs_host.comms.domain_socket import DomainSocket


# --------------------------------------------------------------------------------------------------------------------

uds = None

try:
    uds = DomainSocket('/home/pi/SCS/pipes/display.uds')

    timer = IntervalTimer(10)

    while timer.true():
        now = LocalizedDatetime.now()
        message = "test: %s" % now.as_iso8601()

        uds.connect()
        uds.write(message)

        print(message, file=sys.stderr)
        sys.stderr.flush()


except KeyboardInterrupt:
    print("KeyboardInterrupt", file=sys.stderr)

finally:
    print("exiting", file=sys.stderr)

    if uds:
        uds.close()
