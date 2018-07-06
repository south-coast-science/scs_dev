"""
Created on 5 Jul 2018

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import sys

from scs_core.data.json import JSONify
from scs_core.data.localized_datetime import LocalizedDatetime

from scs_dfe.display.led_state import LEDState

from scs_host.comms.domain_socket import DomainSocket


# --------------------------------------------------------------------------------------------------------------------
# reporter...

class MQTTReporter(object):
    """
    classdocs
    """

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


    def set_led(self, colour):
        if self.__led_uds is None:
            return

        try:
            self.__led_uds.connect(False)
            self.__led_uds.write(JSONify.dumps(LEDState(colour, colour)), False)

        except OSError:
            pass

        finally:
            self.__led_uds.close()


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "MQTTReporter:{verbose:%s, led_uds:%s}" % (self.__verbose, self.__led_uds)
