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

In order to operate effectively in environments with unreliable communications, the aws_mqtt_client buffers messages
prior to publication. The size of the buffer is set by the scs_mfr/mqtt_conf utility.

The aws_mqtt_client utility requires the AWS client authorisation to operate.

Only one MQTT client should run at any one time, per TCP/IP host.

SYNOPSIS
aws_mqtt_client.py [-p UDS_PUB] [-s] { -c { C | G | P | S | X } (UDS_SUB_1) | \
[SUB_TOPIC_1 (UDS_SUB_1) .. SUB_TOPIC_N (UDS_SUB_N)] } [-e] [-l LED_UDS] [-v]

EXAMPLES
( cat < /home/pi/SCS/pipes/mqtt_publication_pipe & ) | \
/home/pi/SCS/scs_dev/src/scs_dev/aws_mqtt_client.py -v -cX  > /home/pi/SCS/pipes/control_subscription_pipe

FILES
~/SCS/aws/aws_client_auth.json
~/SCS/aws/certs/NNNNNNNNNN-certificate.pem.crt
~/SCS/aws/certs/NNNNNNNNNN-private.pem.key
~/SCS/aws/certs/NNNNNNNNNN-public.pem.key
~/SCS/aws/certs/root-CA.crt

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

from scs_core.aws.client.client_auth import ClientAuth
from scs_core.aws.client.mqtt_client import MQTTClient, MQTTSubscriber
from scs_core.aws.config.project import Project

from scs_core.comms.mqtt_conf import MQTTConf

from scs_core.data.publication import Publication

from scs_core.sys.filesystem import Filesystem
from scs_core.sys.signalled_exit import SignalledExit
from scs_core.sys.system_id import SystemID

from scs_dev.cmd.cmd_mqtt_client import CmdMQTTClient

from scs_dev.handler.mqtt_reporter import MQTTReporter
from scs_dev.handler.aws_mqtt_publisher import AWSMQTTPublisher
from scs_dev.handler.aws_mqtt_subscription_handler import AWSMQTTSubscriptionHandler
from scs_dev.handler.uds_reader import UDSReader
from scs_dev.handler.uds_writer import UDSWriter

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    conf = None
    source = None
    reporter = None
    publisher = None


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

        # comms...
        source = UDSReader(cmd.uds_pub)

        if cmd.verbose:
            print("aws_mqtt_client: %s" % source, file=sys.stderr)

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

            if cmd.verbose:
                print("aws_mqtt_client: %s" % project, file=sys.stderr)

            topic = project.channel_path(cmd.channel, system_id)

            # subscriber...
            sub_comms = UDSWriter(cmd.channel_uds)

            handler = AWSMQTTSubscriptionHandler(reporter, sub_comms, cmd.echo)

            subscribers.append(MQTTSubscriber(topic, handler.handle))

        else:
            for subscription in cmd.subscriptions:
                sub_comms = UDSWriter(subscription.address)

                # subscriber...
                handler = AWSMQTTSubscriptionHandler(reporter, sub_comms, cmd.echo)

                if cmd.verbose:
                    print("aws_mqtt_client: %s" % handler, file=sys.stderr)

                subscribers.append(MQTTSubscriber(subscription.topic, handler.handle))

        # client...
        client = MQTTClient(*subscribers)
        publisher = AWSMQTTPublisher(conf, auth, client, reporter)

        if cmd.verbose:
            print("aws_mqtt_client: %s" % publisher, file=sys.stderr)
            sys.stderr.flush()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        # signal handler...
        SignalledExit.construct("aws_mqtt_client", cmd.verbose)

        # client...
        if not conf.inhibit_publishing:
            publisher.connect()

        # data source...
        source.connect()

        # process input...
        for message in source.messages():
            # receive...
            try:
                jdict = json.loads(message)

            except (TypeError, ValueError) as ex:
                reporter.print("%s: %s" % (ex, message))
                continue

            if cmd.echo:
                print(message)
                sys.stdout.flush()

            if conf.inhibit_publishing:
                continue

            publication = Publication.construct_from_jdict(jdict)

            if publication is None:
                continue

            # publish...
            publisher.publish(publication)


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except ConnectionError as ex:
        print("aws_mqtt_client: %s" % ex, file=sys.stderr)

    except (KeyboardInterrupt, SystemExit):
        pass

    finally:
        if cmd and cmd.verbose:
            print("aws_mqtt_client: finishing", file=sys.stderr)

        if source:
            source.close()

        if publisher:
            publisher.disconnect()

        if conf:
            Filesystem.rm(conf.report_file)

        if reporter:
            reporter.print("finished")
