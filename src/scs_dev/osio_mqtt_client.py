#!/usr/bin/env python3

"""
Created on 23 Mar 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The osio_mqtt_client utility is used to subscribe or publish using the OpenSensors.io Community Edition messaging
infrastructure.

Documents for publication are gained from stdin by default, otherwise from the specified Unix domain socket (UDS).
Likewise, documents gained from subscription are written to stdout, or a specified UDS.

Subscriptions can be specified either by a project channel name, or by an explicit messaging topic path. Documents
gained by subscription may be delivered either to stdout, or to a specified Unix domain socket.

The osio_mqtt_client utility requires both the OpenSensors.io API key and client authorisation to operate.

On some system configurations, the success or failure of each message send attempt can be signalled to a two-colour LED.

Only one MQTT client should run at any one time, per TCP/IP host.

SYNOPSIS
osio_mqtt_client.py [-p UDS_PUB] [-s] { -c { C | G | P | S | X } (UDS_SUB_1) | [SUB_TOPIC_1 (UDS_SUB_1) ..
SUB_TOPIC_N (UDS_SUB_N)] } [-e] [-l LED_UDS] [-v]

EXAMPLES
( cat < ~/SCS/pipes/mqtt_publication_pipe & ) | ./osio_mqtt_client.py -v -cX  > ./control_subscription_pipe

FILES
~/SCS/aws/osio_api_auth.json
~/SCS/aws/osio_client_auth.json
~/SCS/aws/osio_project.json

SEE ALSO
scs_dev/led_controller
scs_mfr/mqtt_conf
scs_mfr/osio_api_auth
scs_mfr/osio_client_auth
scs_mfr/osio_host_project

BUGS
When run as a background process, osio_mqtt_client will exit if it has no stdin stream.
"""

import json
import random
import sys
import time

from scs_core.comms.mqtt_conf import MQTTConf

from scs_core.data.json import JSONify
from scs_core.data.publication import Publication
from scs_core.data.queue_report import QueueReport, ClientStatus

from scs_core.osio.client.api_auth import APIAuth
from scs_core.osio.client.client_auth import ClientAuth
from scs_core.osio.config.project import Project
from scs_core.osio.manager.topic_manager import TopicManager

from scs_core.sys.exception_report import ExceptionReport
from scs_core.sys.signalled_exit import SignalledExit
from scs_core.sys.system_id import SystemID

from scs_dev.cmd.cmd_mqtt_client import CmdMQTTClient
from scs_dev.handler.mqtt_reporter import MQTTReporter

from scs_host.client.http_client import HTTPClient
from scs_host.client.mqtt_client import MQTTClient, MQTTSubscriber

from scs_host.comms.domain_socket import DomainSocket
from scs_host.comms.stdio import StdIO

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------
# subscription handler...

class OSIOMQTTHandler(object):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, mqtt_reporter, comms=None, echo=False):
        """
        Constructor
        """
        self.__reporter = mqtt_reporter
        self.__comms = comms
        self.__echo = echo


    # ----------------------------------------------------------------------------------------------------------------

    def handle(self, pub):
        try:
            self.__comms.connect()
            self.__comms.write(JSONify.dumps(pub), False)

        except ConnectionRefusedError:
            self.__reporter.print("connection refused for %s" % self.__comms.address)

        finally:
            self.__comms.close()

        if self.__echo:
            print(JSONify.dumps(pub))
            sys.stdout.flush()

        self.__reporter.print("received: %s" % JSONify.dumps(pub))


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "OSIOMQTTHandler:{reporter:%s, comms:%s, echo:%s}" % (self.__reporter, self.__comms, self.__echo)


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    client = None
    pub_comms = None
    reporter = None


    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdMQTTClient()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print("osio_mqtt_client: %s" % cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # MQTTConf
        conf = MQTTConf.load(Host)

        if cmd.verbose:
            print("osio_mqtt_client: conf: %s" % conf, file=sys.stderr)

        # LED UDS...
        if cmd.led_uds and cmd.verbose:
            print("osio_mqtt_client: led UDS: %s" % cmd.led_uds, file=sys.stderr)

        # APIAuth...
        api_auth = APIAuth.load(Host)

        if api_auth is None:
            print("osio_mqtt_client: APIAuth not available.", file=sys.stderr)
            exit(1)

        if cmd.verbose:
            print("osio_mqtt_client: %s" % api_auth, file=sys.stderr)

        # ClientAuth...
        client_auth = ClientAuth.load(Host)

        if client_auth is None:
            print("osio_mqtt_client: ClientAuth not available.", file=sys.stderr)
            exit(1)

        if cmd.verbose:
            print("osio_mqtt_client: %s" % client_auth, file=sys.stderr)

        # comms...
        pub_comms = DomainSocket(cmd.uds_pub) if cmd.uds_pub else StdIO()

        # manager...
        manager = TopicManager(HTTPClient(), api_auth.api_key)

        # check topics...
        unavailable = False
        for subscription in cmd.subscriptions:
            if not manager.find(subscription.topic):
                print("osio_mqtt_client: Topic not available: %s" % subscription[0], file=sys.stderr)
                unavailable = True

        if unavailable:
            exit(1)

        # reporter...
        reporter = MQTTReporter(cmd.verbose, cmd.led_uds)

        # subscribers...
        subscribers = []

        if cmd.channel:
            # SystemID...
            system_id = SystemID.load(Host)

            if system_id is None:
                print("osio_mqtt_client: SystemID not available.", file=sys.stderr)
                exit(1)

            if cmd.verbose:
                print("osio_mqtt_client: %s" % system_id, file=sys.stderr)

            # Project...
            project = Project.load(Host)

            if project is None:
                print("osio_mqtt_client: Project not available.", file=sys.stderr)
                exit(1)

            topic = project.channel_path(cmd.channel, system_id)

            # handler...
            sub_comms = DomainSocket(cmd.channel_uds) if cmd.channel_uds else StdIO()

            handler = OSIOMQTTHandler(reporter, sub_comms, cmd.echo)

            subscribers.append(MQTTSubscriber(topic, handler.handle))

        else:
            for subscription in cmd.subscriptions:
                sub_comms = DomainSocket(subscription.address) if subscription.address else StdIO()

                # handler...
                handler = OSIOMQTTHandler(reporter, sub_comms, cmd.echo)

                if cmd.verbose:
                    print("osio_mqtt_client: %s" % handler, file=sys.stderr)

                subscribers.append(MQTTSubscriber(subscription.topic, handler.handle))

        # client...
        client = MQTTClient(*subscribers)

        if cmd.verbose:
            print("osio_mqtt_client: %s" % client, file=sys.stderr)

        if cmd.verbose:
            sys.stderr.flush()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        # signal handler...
        SignalledExit.construct("osio_mqtt_client", cmd.verbose)

        pub_comms.connect()

        if not conf.inhibit_publishing:
            client.connect(ClientAuth.MQTT_HOST, client_auth.client_id, client_auth.user_id,
                           client_auth.client_password)

        for message in pub_comms.read():
            # receive...
            try:
                datum = json.loads(message)
            except ValueError:
                reporter.print("bad datum: %s" % message)
                continue

            if cmd.echo:
                print(message)
                sys.stdout.flush()

            if conf.inhibit_publishing:
                continue

            # publish...
            success = False

            while True:
                publication = Publication.construct_from_jdict(datum)

                try:
                    success = client.publish(publication, ClientAuth.MQTT_TIMEOUT)

                    if not success:
                        reporter.print("abandoned")
                        reporter.set_led(QueueReport(0, ClientStatus.CONNECTING, False))

                    break

                except Exception as ex:
                    if cmd.verbose:
                        print(JSONify.dumps(ExceptionReport.construct(ex)))
                        sys.stderr.flush()

                time.sleep(random.uniform(1.0, 2.0))        # Don't hammer the broker!

            if success:
                reporter.print("done")
                reporter.set_led(QueueReport(0, ClientStatus.CONNECTED, True))


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except (BrokenPipeError, ConnectionResetError) as ex:
        print("osio_mqtt_client: %s" % ex, file=sys.stderr)

    except (KeyboardInterrupt, SystemExit):
        pass

    finally:
        if cmd and cmd.verbose:
            print("osio_mqtt_client: finishing", file=sys.stderr)

        if client:
            client.disconnect()

        if pub_comms:
            pub_comms.close()
