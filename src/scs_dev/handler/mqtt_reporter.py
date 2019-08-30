"""
Created on 5 Jul 2018

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

short (connection status)
-----
off         no power        QueueReport.STATUS_NONE
amber       connecting      QueueReport.STATUS_INHIBITED, QueueReport.STATUS_DISCONNECTED
green       connected       QueueReport.STATUS_PUBLISHING, QueueReport.STATUS_CLEARING
red         disconnected    QueueReport.STATUS_QUEUING

long (queue status)
-----
off         no power        QueueReport.STATUS_NONE
amber       clearing        QueueReport.STATUS_CLEARING
green       publishing      QueueReport.STATUS_DISCONNECTED, QueueReport.STATUS_PUBLISHING, QueueReport.STATUS_QUEUING
red         inhibited       QueueReport.STATUS_INHIBITED
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

    __CLIENT_STATUS = {
        QueueStatus.NONE:           ['0', 'R'],
        QueueStatus.INHIBITED:      ['0', 'G'],
        QueueStatus.DISCONNECTED:   ['0', 'A'],
        QueueStatus.PUBLISHING:     ['G', 'G'],
        QueueStatus.QUEUING:        ['R', 'A'],
        QueueStatus.CLEARING:       ['G', 'A']
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

        colours = self.__CLIENT_STATUS[report.status()]

        try:
            self.__led_uds.connect(False)
            self.__led_uds.write(JSONify.dumps(LEDState(colours[0], colours[1])), False)

        except OSError:
            pass

        finally:
            self.__led_uds.close()


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "MQTTReporter:{verbose:%s, led_uds:%s}" % (self.__verbose, self.__led_uds)
