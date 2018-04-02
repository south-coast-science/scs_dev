#!/usr/bin/env python3

"""
Created on 17 Apr 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The XX utility is used to .

EXAMPLES
xx

FILES
~/SCS/aws/

DOCUMENT EXAMPLE
xx

SEE ALSO
scs_dev/


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

from scs_core.sys.shared_secret import SharedSecret
from scs_core.sys.system_id import SystemID

from scs_dev.cmd.cmd_control_receiver import CmdControlReceiver

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # config...

    deferred_commands = ('reboot', 'restart')


    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdControlReceiver()

    if cmd.verbose:
        print(cmd, file=sys.stderr)


    # ------------------------------------------------------------------------------------------------------------
    # resources...

    # SystemID...
    system_id = SystemID.load(Host)

    if system_id is None:
        print("control_receiver: SystemID not available.", file=sys.stderr)
        exit(1)

    if cmd.verbose:
        print(system_id, file=sys.stderr)

    # SharedSecret...
    secret = SharedSecret.load(Host)

    if secret is None:
        print("control_receiver: SharedSecret not available.", file=sys.stderr)
        exit(1)

    if cmd.verbose:
        print(secret, file=sys.stderr)
        sys.stderr.flush()

    system_tag = system_id.message_tag()
    key = secret.key


    try:
        # ------------------------------------------------------------------------------------------------------------
        # run...

        for line in sys.stdin:
            # control...
            try:
                jdict = json.loads(line, object_pairs_hook=OrderedDict)
            except ValueError:
                continue

            try:
                datum = ControlDatum.construct_from_jdict(jdict)
            except TypeError:
                continue

            if datum.attn != system_tag:
                continue

            if cmd.verbose:
                print(datum, file=sys.stderr)
                sys.stderr.flush()

            if not datum.is_valid(key):
                print("control_receiver: invalid digest: %s" % datum, file=sys.stderr)
                sys.stderr.flush()
                continue

            if cmd.echo:
                print(JSONify.dumps(datum))
                sys.stdout.flush()

            # command...
            command = Command.construct_from_tokens(datum.cmd_tokens)

            if command.cmd is not None and not command.is_valid(Host):
                command.error("invalid command")

            # execute immediate commands...
            elif command.cmd not in deferred_commands:
                command.execute(Host)

            # receipt...
            if cmd.receipt:
                now = LocalizedDatetime.now()
                receipt = ControlReceipt.construct_from_datum(datum, now, command, key)

                print(JSONify.dumps(receipt))
                sys.stdout.flush()

                if cmd.verbose:
                    print(JSONify.dumps(receipt), file=sys.stderr)
                    sys.stderr.flush()

            # execute deferred commands...
            if command.cmd in deferred_commands:
                command.execute(Host)


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        if cmd.verbose:
            print("control_receiver: KeyboardInterrupt", file=sys.stderr)
