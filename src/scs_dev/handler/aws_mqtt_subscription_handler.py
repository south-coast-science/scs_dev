"""
Created on 27 Sep 2018

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import json
import sys

from scs_core.data.json import JSONify
from scs_core.data.publication import Publication


# --------------------------------------------------------------------------------------------------------------------
# subscription handler...

class AWSMQTTSubscriptionHandler(object):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, reporter, comms=None, echo=False):
        """
        Constructor
        """
        self.__reporter = reporter
        self.__comms = comms
        self.__echo = echo


    # ----------------------------------------------------------------------------------------------------------------

    # noinspection PyUnusedLocal

    def handle(self, client, userdata, message):
        payload = message.payload.decode()
        payload_jdict = json.loads(payload)

        publication = Publication(message.topic, payload_jdict)

        try:
            self.__comms.connect()
            self.__comms.write(JSONify.dumps(publication), False)

        except ConnectionError:
            self.__reporter.print("connect: %s" % self.__comms.address)

        finally:
            self.__comms.close()

        if self.__echo:
            print(JSONify.dumps(publication))
            sys.stdout.flush()

            self.__reporter.print("received: %s" % JSONify.dumps(publication))


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "AWSMQTTSubscriptionHandler:{reporter:%s, comms:%s, echo:%s}" % \
               (self.__reporter, self.__comms, self.__echo)


