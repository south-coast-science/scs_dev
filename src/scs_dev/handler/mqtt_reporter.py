"""
Created on 5 Jul 2018

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

https://github.com/south-coast-science/docs/wiki/Praxis-LED-colours
"""

import sys

from scs_core.data.json import JSONify
from scs_core.data.localized_datetime import LocalizedDatetime
from scs_core.data.queue_report import QueueReport, QueueStatus

from scs_dfe.led.led_state import LEDState

from scs_host.comms.domain_socket import DomainSocket


# --------------------------------------------------------------------------------------------------------------------

class MQTTReporter(object):
    """
    classdocs
    """

    __QUEUE_STATE = {
        QueueStatus.NONE:               ['R', '0'],
        QueueStatus.INHIBITED:          ['G', '0'],
        QueueStatus.STARTING:           ['A', '0'],
        QueueStatus.CONNECTING:         ['G', 'A'],
        QueueStatus.WAITING_FOR_DATA:   ['G', 'A'],
        QueueStatus.PUBLISHING:         ['G', 'G'],
        QueueStatus.CLEARING:           ['G', 'G'],
        QueueStatus.QUEUING:            ['G', 'R']
    }

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, verbose, led_uds_name=None):
        """
        Constructor
        """
        self.__verbose = verbose
        self.__led_uds = DomainSocket(led_uds_name) if led_uds_name else None


    # ----------------------------------------------------------------------------------------------------------------

    def print(self, status):
        if not self.__verbose:
            return

        now = LocalizedDatetime.now()
        print("%s:         mqtt: %s" % (now.as_time(), status), file=sys.stderr)
        sys.stderr.flush()


    def set_led(self, report: QueueReport):
        if self.__led_uds is None:
            return

        colours = self.__QUEUE_STATE[report.queue_state()]

        try:
            self.__led_uds.connect()
            self.__led_uds.write(JSONify.dumps(LEDState(colours[0], colours[1])), False)

        except OSError:
            pass

        finally:
            self.__led_uds.close()


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "MQTTReporter:{verbose:%s, led_uds:%s}" % (self.__verbose, self.__led_uds)
