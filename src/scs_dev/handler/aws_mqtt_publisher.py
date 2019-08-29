"""
Created on 27 Sep 2018

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import json
import time

from collections import OrderedDict
from multiprocessing import Manager

from AWSIoTPythonSDK.exception.operationError import operationError
from AWSIoTPythonSDK.exception.operationTimeoutException import operationTimeoutException

from scs_core.aws.client.client_auth import ClientAuth
from scs_core.aws.client.mqtt_client import MQTTClient

from scs_core.comms.mqtt_conf import MQTTConf

from scs_core.data.message_queue import MessageQueue
from scs_core.data.publication import Publication
from scs_core.data.queue_report import QueueReport

from scs_core.sync.synchronised_process import SynchronisedProcess

from scs_dev.handler.mqtt_reporter import MQTTReporter


# --------------------------------------------------------------------------------------------------------------------

class AWSMQTTPublisher(SynchronisedProcess):
    """
    classdocs
    """

    __QUEUE_INSPECTION_INTERVAL =   2.0

    __CONNECT_TIME =                3.0         # seconds
    __CONNECT_RETRY_TIME =          2.0         # seconds

    __POST_PUBLISH_TIME =           0.1         # seconds - was 0.5


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, conf: MQTTConf, auth: ClientAuth, queue: MessageQueue, client: MQTTClient,
                 reporter: MQTTReporter):
        """
        Constructor
        """
        manager = Manager()

        SynchronisedProcess.__init__(self, AWSMQTTReport(manager.dict()))

        initial_state = QueueReport.CLIENT_INHIBITED if conf.inhibit_publishing else QueueReport.CLIENT_DISCONNECTED
        self.__state = AWSMQTTState(initial_state, reporter)

        self.__conf = conf
        self.__auth = auth
        self.__queue = queue
        self.__client = client
        self.__reporter = reporter

        self.__report = QueueReport(0, initial_state, False)
        self.__report.save(self.__conf.report_file)


    # ----------------------------------------------------------------------------------------------------------------
    # SynchronisedProcess implementation...

    def run(self):
        try:
            while True:
                self.__process_messages()
                time.sleep(self.__QUEUE_INSPECTION_INTERVAL)

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
            self.__report.length = self.__queue.length()

            if self.__report.length < 1:
                return

            if self.__conf.report_file:
                self.__report.save(self.__conf.report_file)

            self.__reporter.print("queue: %s" % self.__report.length)

            try:
                self.__process_message(self.__next_message())

            except Exception as ex:
                self.__reporter.print("pms: %s" % ex.__class__.__name__)


    def __process_message(self, publication):
        if publication is None:
            self.__queue.dequeue()
            return

        self.__report.client_state = self.__state.state

        if self.__report.client_state == QueueReport.CLIENT_INHIBITED:
            # discard...
            self.__queue.dequeue()
            return

        if self.__report.client_state == QueueReport.CLIENT_DISCONNECTED:
            # connect...
            if self.__connect():
                self.__state.set_connected()
                time.sleep(self.__CONNECT_TIME)

            else:
                time.sleep(self.__CONNECT_RETRY_TIME)

            return

        if self.__report.client_state == QueueReport.CLIENT_CONNECTED:
            # publish...
            self.__publish_message(publication)
            self.__queue.dequeue()

            time.sleep(self.__POST_PUBLISH_TIME)

            return

        else:
            raise ValueError("unknown AWSMQTTState: %s" % self.__report.client_state)


    # ----------------------------------------------------------------------------------------------------------------
    # connection management...

    def __connect(self):
        try:
            success = self.__client.connect(self.__auth)

            if success:
                self.__reporter.print("connect: done")
                self.__reporter.set_led("G")
                return True

            else:
                self.__reporter.print("connect: failed")
                self.__reporter.set_led("R")
                return False

        except OSError as ex:
            self.__reporter.print("connect: %s" % ex)
            self.__reporter.set_led("R")
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
        self.__report.publish_success = False

        try:
            start_time = time.time()

            paho = self.__client.publish(publication)
            elapsed_time = time.time() - start_time

            self.__reporter.print("paho: %s: %0.3f" % ("1" if paho else "0", elapsed_time))
            self.__reporter.set_led("G")

            self.__report.publish_success = True

        except (OSError, operationError) as ex:
            self.__reporter.print("pm: %s" % ex.__class__.__name__)
            self.__reporter.set_led("R")

        except operationTimeoutException:
            self.__reporter.set_led("R")


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "AWSMQTTPublisher:{state:%s, conf:%s, auth:%s, queue:%s, client:%s, reporter:%s, report:%s}" % \
               (self.__state, self.__conf, self.__auth, self.__queue, self.__client, self.__reporter, self.__report)


# --------------------------------------------------------------------------------------------------------------------

class AWSMQTTState(object):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, state, reporter):
        """
        Constructor
        """
        self.__state = state
        self.__reporter = reporter

        self.__latest_success = None


    # ----------------------------------------------------------------------------------------------------------------

    def set_connected(self):
        self.__latest_success = time.time()

        if self.__state == QueueReport.CLIENT_CONNECTED:
            return

        self.__state = QueueReport.CLIENT_CONNECTED
        self.__reporter.print("-> CONNECTED")


    def set_disconnected(self):
        self.__latest_success = None

        self.__state = QueueReport.CLIENT_DISCONNECTED
        self.__reporter.print("-> DISCONNECTED")


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def state(self):
        return self.__state


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "AWSMQTTState:{state:%s, latest_success:%s}}" %  (self.__state, self.__latest_success)


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
