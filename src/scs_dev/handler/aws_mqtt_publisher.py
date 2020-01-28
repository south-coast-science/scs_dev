"""
Created on 27 Sep 2018

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import time

from AWSIoTPythonSDK.exception.operationTimeoutException import operationTimeoutException

from scs_core.aws.client.client_auth import ClientAuth
from scs_core.aws.client.mqtt_client import MQTTClient

from scs_core.comms.mqtt_conf import MQTTConf

from scs_core.data.queue_report import QueueReport, ClientStatus

from scs_dev.handler.mqtt_reporter import MQTTReporter


# --------------------------------------------------------------------------------------------------------------------

class AWSMQTTPublisher(object):
    """
    classdocs
    """

    __CONNECT_TIME =                3.0         # seconds
    __CONNECT_RETRY_TIME =         10.0         # seconds


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, conf: MQTTConf, auth: ClientAuth, client: MQTTClient, reporter: MQTTReporter):
        """
        Constructor
        """
        self.__conf = conf
        self.__auth = auth
        self.__client = client
        self.__reporter = reporter

        # report...
        client_state = ClientStatus.INHIBITED if conf.inhibit_publishing else ClientStatus.WAITING
        self.__status = QueueReport(0, client_state, False)
        self.__report()


    # ----------------------------------------------------------------------------------------------------------------

    def connect(self):
        if self.__conf.inhibit_publishing:
            return

        # report...
        self.__status.client_state = ClientStatus.CONNECTING
        self.__report()

        # connect...
        while not self.__client.connect(self.__auth, self.__conf.debug):
            self.__reporter.print("connect: failed")
            time.sleep(self.__CONNECT_RETRY_TIME)

        time.sleep(self.__CONNECT_TIME)

        # report...
        self.__reporter.print("connect: done")
        self.__status.client_state = ClientStatus.CONNECTED
        self.__report()


    def disconnect(self):
        if self.__conf.inhibit_publishing:
            return

        # disconnect...
        self.__client.disconnect()

        # report...
        self.__reporter.print("disconnect: done")
        self.__status.client_state = ClientStatus.WAITING
        self.__report()


    def publish(self, publication):
        if self.__conf.inhibit_publishing:
            return

        # report...
        self.__status.length = 1                # indicate that document(s) have been presented for publication

        # publish...
        while True:
            try:
                start = time.time()
                reached_paho = self.__client.publish(publication)
                elapsed = time.time() - start

                self.__reporter.print("paho: %s: %0.3f" % ("1" if reached_paho else "0", elapsed))
                break

            except operationTimeoutException:
                # report...
                self.__status.publish_success = False
                self.__report()

        # report...
        self.__status.publish_success = True
        self.__report()


    # ----------------------------------------------------------------------------------------------------------------

    def __report(self):
        self.__status.save(self.__conf.report_file)
        self.__reporter.set_led(self.__status)


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "AWSMQTTPublisher:{conf:%s, auth:%s, client:%s, reporter:%s, report:%s}" % \
               (self.__conf, self.__auth, self.__client, self.__reporter, self.__status)
