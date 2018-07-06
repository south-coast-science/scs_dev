#!/usr/bin/env python3

"""
Created on 4 Oct 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The aws_mqtt_client utility is used to subscribe or publish using the South Coast Science / AWS messaging
infrastructure.

Documents for publication are gained from stdin by default, otherwise from the specified Unix domain socket (UDS).
Likewise, documents gained from subscription are written to stdout, or a specified UDS.

Subscriptions can be specified either by a project channel name, or by an explicit messaging topic path. Documents
gained by subscription may be delivered either to stdout, or to a specified Unix domain socket.

The aws_mqtt_client utility requires the AWS client authorisation to operate.

Only one MQTT client should run at any one time, per TCP/IP host.

SYNOPSIS
aws_mqtt_client.py [-p UDS_PUB] [-s] { -c { C | G | P | S | X } (UDS_SUB_1) |
[SUB_TOPIC_1 (UDS_SUB_1) .. SUB_TOPIC_N (UDS_SUB_N)] } [-e] [-l LED_UDS] [-v]

EXAMPLES
( cat < /home/pi/SCS/pipes/mqtt_publication_pipe & ) | \
/home/pi/SCS/scs_dev/src/scs_dev/aws_mqtt_client.py -v -cX  > /home/pi/SCS/pipes/control_subscription_pipe

FILES
~/SCS/aws/aws_client_auth.json

SEE ALSO
scs_dev/led_controller
scs_mfr/mqtt_conf
scs_mfr/aws_client_auth
scs_mfr/aws_project

BUGS
When run as a background process, aws_mqtt_client will exit if it has no stdin stream.
"""

import json
import sys

from collections import OrderedDict

from scs_core.aws.client.client_auth import ClientAuth
from scs_core.aws.client.mqtt_client import MQTTClient, MQTTSubscriber
from scs_core.aws.config.project import Project

from scs_core.comms.mqtt_conf import MQTTConf

from scs_core.data.json import JSONify
from scs_core.data.publication import Publication

from scs_core.sys.system_id import SystemID

from scs_dev.cmd.cmd_mqtt_client import CmdMQTTClient
from scs_dev.reporter.mqtt_reporter import MQTTReporter

from scs_host.comms.domain_socket import DomainSocket
from scs_host.comms.stdio import StdIO

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------
# subscription handler...

class AWSMQTTHandler(object):
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

    def handle(self, *_):                       # params: client, userdata, message
        payload = message.payload.decode()
        payload_jdict = json.loads(payload, object_pairs_hook=OrderedDict)

        pub = Publication(message.topic, payload_jdict)

        try:
            self.__comms.connect()
            self.__comms.write(JSONify.dumps(pub), False)

        except ConnectionRefusedError:
            reporter.print("connection refused for %s" % self.__comms.address)

        finally:
            self.__comms.close()

        if self.__echo:
            print(JSONify.dumps(pub))
            sys.stdout.flush()

        reporter.print("received: %s" % JSONify.dumps(pub))


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "AWSMQTTHandler:{reporter:%s, comms:%s, echo:%s}" % \
               (self.__reporter, self.__comms, self.__echo)


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
        print("aws_mqtt_client: %s" % cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # MQTTConf
        conf = MQTTConf.load(Host)

        if cmd.verbose:
            print("aws_mqtt_client: conf: %s" % conf, file=sys.stderr)

        # LED UDS...
        if cmd.led_uds and cmd.verbose:
            print("aws_mqtt_client: led UDS: %s" % cmd.led_uds, file=sys.stderr)

        # ClientAuth...
        auth = ClientAuth.load(Host)

        if auth is None:
            print("aws_mqtt_client: ClientAuth not available.", file=sys.stderr)
            exit(1)

        if cmd.verbose:
            print("aws_mqtt_client: %s" % auth, file=sys.stderr)

        # comms...
        pub_comms = DomainSocket(cmd.uds_pub_addr) if cmd.uds_pub_addr else StdIO()

        # reporter...
        reporter = MQTTReporter(cmd.verbose, cmd.led_uds)

        # subscribers...
        subscribers = []

        if cmd.channel:
            # SystemID...
            system_id = SystemID.load(Host)

            if system_id is None:
                print("aws_mqtt_client: SystemID not available.", file=sys.stderr)
                exit(1)

            if cmd.verbose:
                print("aws_mqtt_client: %s" % system_id, file=sys.stderr)

            # Project...
            project = Project.load(Host)

            if project is None:
                print("aws_mqtt_client: Project not available.", file=sys.stderr)
                exit(1)

            topic = project.channel_path(cmd.channel, system_id)

            # handler...
            sub_comms = DomainSocket(cmd.channel_uds) if cmd.channel_uds else StdIO()

            handler = AWSMQTTHandler(reporter, sub_comms, cmd.echo)

            subscribers.append(MQTTSubscriber(topic, handler.handle))

        else:
            for subscription in cmd.subscriptions:
                sub_comms = DomainSocket(subscription.address) if subscription.address else StdIO()

                # handler...
                handler = AWSMQTTHandler(reporter, sub_comms, cmd.echo)

                if cmd.verbose:
                    print("aws_mqtt_client: %s" % handler, file=sys.stderr)

                subscribers.append(MQTTSubscriber(subscription.topic, handler.handle))

        # client...
        client = MQTTClient(*subscribers)

        if cmd.verbose:
            print("aws_mqtt_client: %s" % client, file=sys.stderr)

        if cmd.verbose:
            sys.stderr.flush()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        reporter.set_led("A")

        pub_comms.connect()

        if not conf.inhibit_publishing:
            client.connect(auth)

        for message in pub_comms.read():
            # receive...
            try:
                jdict = json.loads(message, object_pairs_hook=OrderedDict)
            except ValueError:
                reporter.print("bad datum: %s" % message)
                continue

            if cmd.echo:
                print(message)
                sys.stdout.flush()

            if conf.inhibit_publishing:
                continue

            # publish...
            publication = Publication.construct_from_jdict(jdict)

            success = client.publish(publication)

            if success:
                reporter.print("done")
                reporter.set_led("G")

            else:
                reporter.print("abandoned")
                reporter.set_led("R")


        # ----------------------------------------------------------------------------------------------------------------
        # end...

    except KeyboardInterrupt:
        if cmd.verbose:
            print("aws_mqtt_client: KeyboardInterrupt", file=sys.stderr)

    finally:
        if client:
            client.disconnect()

        if pub_comms:
            pub_comms.close()

        if reporter:
            reporter.set_led("A")
