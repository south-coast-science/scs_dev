#!/usr/bin/env python3

"""
Created on 5 Dec 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

Requires DeviceID document.

command line example:
./scs_dev/particulates_sampler.py -i 10 | \
./scs_dev/osio_topic_publisher.py -e /users/southcoastscience-dev/test/particulates
"""

import sys

from scs_core.data.json import JSONify
from scs_core.data.localized_datetime import LocalizedDatetime
from scs_core.sys.device_id import DeviceID
from scs_core.sys.exception_report import ExceptionReport

from scs_dev.cmd.cmd_sampler import CmdSampler
from scs_dev.sampler.particulates_sampler import ParticulatesSampler

from scs_host.bus.i2c import I2C
from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    io = None
    sampler = None

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSampler(10)

    log_file = open(cmd.log, 'a') if cmd.log else None

    if cmd.verbose:
        print(cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resource...

        I2C.open(Host.I2C_SENSORS)


        device_id = DeviceID.load_from_host(Host)

        if device_id is None:
            print("DeviceID not available.", file=sys.stderr)
            exit()

        if cmd.verbose:
            print(device_id, file=sys.stderr)


        sampler = ParticulatesSampler(device_id, cmd.interval, cmd.samples)

        if cmd.verbose:
            print(sampler, file=sys.stderr)

        sampler.on()
        sampler.reset_timer()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        for sample in sampler.samples():
            if cmd.log:
                log_file.write("%s: rec: %s\n" % (LocalizedDatetime.now().as_iso8601(), sample.rec.as_iso8601()))
                log_file.flush()

            print(JSONify.dumps(sample))
            sys.stdout.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt as ex:
        if cmd.verbose:
            print("particulates_sampler: KeyboardInterrupt", file=sys.stderr)

    except Exception as ex:
        if cmd.log:
            log_file.write("%s: except: %s\n" % (LocalizedDatetime.now().as_iso8601(), ex))
            log_file.flush()

        print(JSONify.dumps(ExceptionReport.construct(ex)), file=sys.stderr)

    finally:
        if sampler:
            sampler.off()

        I2C.close()

        if cmd.log:
            log_file.close()
