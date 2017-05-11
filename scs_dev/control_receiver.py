#!/usr/bin/env python3

"""
Created on 17 Apr 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

Warning: osio_mqtt_client should be started before control_receiver.

command line example:
cat ~/SCS/pipes/control_subscription_pipe | ./osio_topic_subscriber.py -cX | ./control_receiver.py -r -v | \
./osio_topic_publisher.py -cX > ~/SCS/pipes/control_publication_pipe 
"""

import json
import sys

from collections import OrderedDict

from scs_core.control.command import Command
from scs_core.control.control_datum import ControlDatum
from scs_core.control.control_receipt import ControlReceipt

from scs_core.data.json import JSONify
from scs_core.data.localized_datetime import LocalizedDatetime

from scs_core.sys.exception_report import ExceptionReport
from scs_core.sys.system_id import SystemID

from scs_dev.cmd.cmd_control_receiver import CmdControlReceiver

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdControlReceiver()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit()

    if cmd.verbose:
        print(cmd, file=sys.stderr)

    # ------------------------------------------------------------------------------------------------------------
    # resources...

    if cmd.tag:
        tag = cmd.tag
        subscriber_sn = cmd.serial_number

    else:
        # SystemID...
        system_id = SystemID.load_from_host(Host)

        if system_id is None:
            print("SystemID not available.", file=sys.stderr)
            exit()

        if cmd.verbose:
            print(system_id, file=sys.stderr)
            sys.stderr.flush()

        tag = system_id.message_tag()
        subscriber_sn = Host.serial_number()


    try:
        # ------------------------------------------------------------------------------------------------------------
        # run...

        for line in sys.stdin:
            jdict = json.loads(line, object_pairs_hook=OrderedDict)

            try:
                datum = ControlDatum.construct_from_jdict(jdict)
            except TypeError:
                continue

            if datum.attn != tag:
                continue

            if cmd.verbose:
                print(datum, file=sys.stderr)
                sys.stderr.flush()

            if not datum.is_valid(subscriber_sn):
                print("control_receiver: invalid digest: %s" % datum, file=sys.stderr)
                continue

            if cmd.echo:
                print(JSONify.dumps(datum))
                sys.stdout.flush()

            command = Command.construct_from_tokens(datum.cmd_tokens)
            command.execute(Host)

            if cmd.receipt:
                now = LocalizedDatetime.now()
                receipt = ControlReceipt.construct_from_datum(datum, now, command, subscriber_sn)

                print(JSONify.dumps(receipt))
                sys.stdout.flush()

                if cmd.verbose:
                    print(receipt, file=sys.stderr)
                    sys.stderr.flush()

            # TODO: perform reboot commands here


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt as ex:
        if cmd.verbose:
            print("control_receiver: KeyboardInterrupt", file=sys.stderr)

    except Exception as ex:
        print(JSONify.dumps(ExceptionReport.construct(ex)), file=sys.stderr)
