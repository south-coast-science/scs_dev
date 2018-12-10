"""
Created on 27 Sep 2018

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import json
import time

from collections import OrderedDict

from multiprocessing import Manager

from scs_core.aws.client.client_auth import ClientAuth
from scs_core.aws.client.mqtt_client import MQTTClient

from scs_core.comms.mqtt_conf import MQTTConf

from scs_core.data.message_queue import MessageQueue
from scs_core.data.publication import Publication

from scs_core.sync.synchronised_process import SynchronisedProcess

from scs_dev.handler.mqtt_reporter import MQTTReporter


# --------------------------------------------------------------------------------------------------------------------

class AWSMQTTPublisher(SynchronisedProcess):
    """
    classdocs
    """

    __RETRY_TIME =              2.0         # seconds
    __CONNECT_TIME =            3.0         # seconds
    __POST_PUBLISH_TIME =       0.5         # seconds

    __TIMEOUT =                 120.0       # seconds


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, conf: MQTTConf, auth: ClientAuth, queue: MessageQueue, client: MQTTClient,
                 reporter: MQTTReporter):
        """
        Constructor
        """
        manager = Manager()

        SynchronisedProcess.__init__(self, AWSMQTTReport(manager.dict()))

        initial_state = AWSMQTTState.INHIBITED if conf.inhibit_publishing else AWSMQTTState.DISCONNECTED
        self.__state = AWSMQTTState(initial_state, self.__TIMEOUT, reporter)

        self.__conf = conf
        self.__auth = auth
        self.__queue = queue
        self.__client = client
        self.__reporter = reporter


    # ----------------------------------------------------------------------------------------------------------------
    # SynchronisedProcess implementation...

    def run(self):
        try:
            while True:
                self.__process_messages()
                time.sleep(self.__RETRY_TIME)                   # don't hammer the CPU

        except KeyboardInterrupt:
            pass


    def stop(self):
        self.__disconnect()
        self.__state.set_disconnected()

        super().stop()


    # ----------------------------------------------------------------------------------------------------------------
    # state management...

    def __process_messages(self):
        while True:
            queue_length = self.__queue.length()

            if queue_length < 1:
                return

            self.__reporter.print("queue: %s" % queue_length)

            self.__process_message(self.__next_message())


    def __process_message(self, publication):
        if publication is None:
            self.__queue.dequeue()
            return

        state = self.__state.state

        if state == AWSMQTTState.INHIBITED:
            # discard...
            self.__queue.dequeue()
            return

        if state == AWSMQTTState.DISCONNECTED:
            # connect...
            if self.__connect():
                self.__state.set_connected()

                time.sleep(self.__CONNECT_TIME)

            return

        if state == AWSMQTTState.CONNECTED:
            # publish...
            if self.__publish_message(publication):
                self.__state.set_connected()
                self.__queue.dequeue()

                time.sleep(self.__POST_PUBLISH_TIME)

            else:
                time.sleep(self.__RETRY_TIME)

            return

        else:
            raise ValueError("unknown AWSMQTTState: %s" % state)


    # ----------------------------------------------------------------------------------------------------------------
    # connection management...

    def __connect(self):
        try:
            if self.__client.connect(self.__auth):
                self.__reporter.print("connect: done")
                return True

            self.__reporter.print("connect: failed")
            return False

        except OSError as ex:
            self.__reporter.print("connect: %s" % ex)
            return False


    def __disconnect(self):
        self.__client.disconnect()


    # ----------------------------------------------------------------------------------------------------------------
    # message management...

    def __next_message(self):
        message = self.__queue.next()

        try:
            datum = json.loads(message, object_pairs_hook=OrderedDict)

            return Publication.construct_from_jdict(datum)

        except (TypeError, ValueError) as ex:
            self.__reporter.print("next_message: %s" % ex)

            return None


    def __publish_message(self, publication):
        try:
            start_time = time.time()

            if self.__client.publish(publication):
                elapsed_time = time.time() - start_time

                self.__reporter.print("done: %0.3f" % elapsed_time)
                self.__reporter.set_led("G")

                return True

            self.__reporter.print("failed")
            self.__reporter.set_led("R")

            return False

        except OSError as ex:
            self.__reporter.print("publish_message: %s" % ex)
            self.__reporter.set_led("R")

            return False


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "AWSMQTTPublisher:{state:%s, conf:%s, auth:%s, queue:%s, client:%s, reporter:%s}" % \
               (self.__state, self.__conf, self.__auth, self.__queue, self.__client, self.__reporter)


# --------------------------------------------------------------------------------------------------------------------

class AWSMQTTState(object):
    """
    classdocs
    """

    INHIBITED =         1
    DISCONNECTED =      2
    CONNECTED =         3


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, state, timeout, reporter):
        """
        Constructor
        """
        self.__state = state
        self.__timeout = timeout
        self.__reporter = reporter

        self.__latest_success = None


    # ----------------------------------------------------------------------------------------------------------------

    def set_connected(self):
        self.__latest_success = time.time()

        if self.__state == self.CONNECTED:
            return

        self.__state = self.CONNECTED
        self.__reporter.print("-> CONNECTED")


    def set_disconnected(self):
        self.__latest_success = None

        self.__state = self.DISCONNECTED
        self.__reporter.print("-> DISCONNECTED")


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def state(self):
        if self.__state != self.CONNECTED:
            return self.__state

        if time.time() - self.__latest_success > self.__timeout:
            self.set_disconnected()

        return self.__state


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "AWSMQTTState:{state:%s, timeout:%s, latest_success:%s}}" % \
               (self.__state, self.__timeout, self.__latest_success)


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
        return "AWSMQTTReport:{pub_time:%s, queue_length:%s}}" % (self.pub_time, self.queue_length)
