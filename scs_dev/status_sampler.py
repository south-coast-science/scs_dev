#!/usr/bin/env python3

"""
Created on 5 Dec 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

Requires DeviceID document.

command line example:
./scs_dev/status_sampler.py -i 10 | ./scs_dev/osio_topic_publisher.py -e /users/southcoastscience-dev/test/status
"""

import sys

from scs_core.data.json import JSONify
from scs_core.data.localized_datetime import LocalizedDatetime
from scs_core.sys.device_id import DeviceID
from scs_core.sys.exception_report import ExceptionReport

from scs_dev.cmd.cmd_sampler import CmdSampler
from scs_dev.sampler.status_sampler import StatusSampler

from scs_dfe.gps.pam7q import PAM7Q

from scs_host.bus.i2c import I2C
from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSampler(10)

    log_file = open(cmd.log, 'a') if cmd.log else None

    if cmd.verbose:
        print(cmd, file=sys.stderr)

    try:
        I2C.open(Host.I2C_SENSORS)

        # ------------------------------------------------------------------------------------------------------------
        # resource...

        device_id = DeviceID.load_from_host(Host)

        if device_id is None:
            print("DeviceID not available.", file=sys.stderr)
            exit()

        if cmd.verbose:
            print(device_id, file=sys.stderr)


        gps = PAM7Q()
        gps.power_on()

        sampler = StatusSampler(device_id, cmd.interval, cmd.samples)

        if cmd.verbose:
            print(sampler, file=sys.stderr)


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
            print("status_sampler: KeyboardInterrupt", file=sys.stderr)

    except Exception as ex:
        if cmd.log:
            report = JSONify.dumps(ExceptionReport.construct(ex))
            log_file.write("%s: %s\n" % (LocalizedDatetime.now().as_iso8601(), report))
            log_file.flush()

        print(JSONify.dumps(ExceptionReport.construct(ex)), file=sys.stderr)

    finally:
        I2C.close()

        if cmd.log:
            log_file.close()
