"""
Created on 27 Sep 2018

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import json
import time

from collections import OrderedDict

from scs_core.data.publication import Publication
from scs_core.sync.synchronised_process import SynchronisedProcess


# --------------------------------------------------------------------------------------------------------------------

class AWSMQTTPublisher(SynchronisedProcess):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, conf, auth, queue, client, reporter):
        """
        Constructor
        """
        SynchronisedProcess.__init__(self)

        self.__conf = conf
        self.__auth = auth
        self.__queue = queue
        self.__client = client
        self.__reporter = reporter


    # ----------------------------------------------------------------------------------------------------------------
    # SynchronisedProcess implementation...

    def run(self):
        try:
            self.__connect()

            while True:
                self.__publish_messages()

        except KeyboardInterrupt:
            pass


    def stop(self):
        self.__disconnect()
        super().stop()


    # ----------------------------------------------------------------------------------------------------------------

    def __connect(self):
        if self.__conf.inhibit_publishing:
            return

        # MQTT connect...
        while True:
            try:
                if self.__client.connect(self.__auth):
                    time.sleep(2.0)                             # wait for stabilisation
                    break

                self.__reporter.print("connect: failed")

            except OSError as ex:
                self.__reporter.print("connect: %s" % ex)

            time.sleep(2.0)                                     # wait for retry

        self.__reporter.print("connect: done")


    def __disconnect(self):
        if self.__conf.inhibit_publishing:
            return

        self.__client.disconnect()


    def __publish_messages(self):
        if self.__conf.inhibit_publishing:
            return

        while self.__queue.length() > 0:
            # retrieve message...
            message = self.__queue.oldest()
            datum = json.loads(message, object_pairs_hook=OrderedDict)

            # MQTT publish...
            publication = Publication.construct_from_jdict(datum)

            while True:
                try:
                    start_time = time.time()

                    if self.__client.publish(publication):
                        elapsed_time = time.time() - start_time

                        self.__queue.remove_oldest()

                        self.__reporter.print("done: %0.3f" % elapsed_time)
                        self.__reporter.set_led("G")

                        time.sleep(0.2)                         # wait for the queue
                        break

                    self.__reporter.print("failed")
                    self.__reporter.set_led("R")

                except OSError as ex:
                    self.__reporter.print("publish: %s" % ex)
                    self.__reporter.set_led("R")

                time.sleep(2.0)                                 # wait for auto-reconnect



    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "AWSMQTTPublisher:{conf:%s, auth:%s, queue:%s, client:%s, reporter:%s}" % \
               (self.__conf, self.__auth, self.__queue, self.__client, self.__reporter)
