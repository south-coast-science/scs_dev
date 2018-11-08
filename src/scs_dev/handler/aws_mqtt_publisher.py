"""
Created on 27 Sep 2018

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import json
import time

from collections import OrderedDict

from multiprocessing import Manager

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
        manager = Manager()

        SynchronisedProcess.__init__(self, AWSMQTTReport(manager.dict()))

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
                time.sleep(2.0)                                 # don't hammer the CPU

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

        while True:
            queue_length = self.__queue.length()

            if queue_length < 1:
                return

            self.__reporter.print("queue: %s" % queue_length)

            # retrieve...
            message = self.__queue.next()

            try:
                datum = json.loads(message, object_pairs_hook=OrderedDict)

            except (TypeError, ValueError) as ex:
                self.__reporter.print("datum: %s" % ex)
                self.__queue.dequeue()
                return

            # MQTT publish...
            publication = Publication.construct_from_jdict(datum)

            while True:
                try:
                    start_time = time.time()

                    if self.__client.publish(publication):
                        elapsed_time = time.time() - start_time

                        self.__queue.dequeue()

                        self.__reporter.print("done: %0.3f" % elapsed_time)
                        self.__reporter.set_led("G")
                        break

                    self.__reporter.print("failed")     # TODO: attempt a reconnect (at least for diagnostic purposes)
                    self.__reporter.set_led("R")

                except OSError as ex:
                    self.__reporter.print("publish: %s" % ex)
                    self.__reporter.set_led("R")

                time.sleep(2.0)                                 # wait for auto-reconnect


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "AWSMQTTPublisher:{conf:%s, auth:%s, queue:%s, client:%s, reporter:%s}" % \
               (self.__conf, self.__auth, self.__queue, self.__client, self.__reporter)


# --------------------------------------------------------------------------------------------------------------------

class AWSMQTTReport(object):
    """
    classdocs
    """

    __PUB_TIME =            'pub_time'
    __QUEUE_LENGTH =        'queue_length'


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, value):
        """
        Constructor
        """
        self.__value = value

        self.pub_time = 0
        self.queue_length = 0


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def pub_time(self):
        return self.__value[self.__PUB_TIME]


    @pub_time.setter
    def pub_time(self, pub_time):
        self.__value[self.__PUB_TIME] = pub_time


    @property
    def queue_length(self):
        return self.__value[self.__QUEUE_LENGTH]


    @queue_length.setter
    def queue_length(self, queue_length):
        self.__value[self.__QUEUE_LENGTH] = queue_length


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "AWSMQTTReport:{pub_time:%s, queue_length:%s}}" % \
               (self.pub_time, self.queue_length)
