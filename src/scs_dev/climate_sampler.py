#!/usr/bin/env python3

"""
Created on 18 Feb 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The xx utility .

EXAMPLES
./status_sampler.py -i10 | ./aws_topic_publisher.py -e -cS

FILES
~/SCS/xx

DOCUMENT EXAMPLE
{"api-key": "de92c5ff-b47a-4cc4-a04c-62d684d74a1f"}

SEE ALSO
scs_dev/aws_topic_subscriber


Requires SystemID document.

command line example:
./climate_sampler.py -i 5 | ./osio_topic_publisher.py -e /users/southcoastscience-dev/test/climate
"""

import sys

from scs_core.data.json import JSONify
from scs_core.data.localized_datetime import LocalizedDatetime

from scs_core.sync.timed_runner import TimedRunner

from scs_core.sys.system_id import SystemID
from scs_core.sys.exception_report import ExceptionReport

from scs_dev.cmd.cmd_sampler import CmdSampler
from scs_dev.sampler.climate_sampler import ClimateSampler

from scs_dfe.climate.sht_conf import SHTConf

from scs_host.bus.i2c import I2C
from scs_host.sync.schedule_runner import ScheduleRunner
from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSampler()

    if cmd.verbose:
        print(cmd, file=sys.stderr)

    try:
        I2C.open(Host.I2C_SENSORS)


        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # SystemID...
        system_id = SystemID.load(Host)

        if system_id is None:
            print("climate_sampler: SystemID not available.", file=sys.stderr)
            exit(1)

        if cmd.verbose:
            print(system_id, file=sys.stderr)

        # SHTConf...
        sht_conf = SHTConf.load(Host)

        if sht_conf is None:
            print("climate_sampler: SHTConf not available.", file=sys.stderr)
            exit(1)

        if cmd.verbose:
            print(sht_conf, file=sys.stderr)

        # SHT...
        sht = sht_conf.ext_sht()

        # runner...
        runner = TimedRunner(cmd.interval, cmd.samples) if cmd.semaphore is None \
            else ScheduleRunner(cmd.semaphore, False)

        sampler = ClimateSampler(runner, system_id.message_tag(), sht)

        if cmd.verbose:
            print(sampler, file=sys.stderr)
            sys.stderr.flush()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        for sample in sampler.samples():
            if cmd.verbose:
                now = LocalizedDatetime.now()
                print("%s:      climate: %s" % (now.as_iso8601(), sample.rec.as_iso8601()), file=sys.stderr)
                sys.stderr.flush()

            print(JSONify.dumps(sample))
            sys.stdout.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        if cmd.verbose:
            print("climate_sampler: KeyboardInterrupt", file=sys.stderr)

    except Exception as ex:
        print(JSONify.dumps(ExceptionReport.construct(ex)), file=sys.stderr)

    finally:
        I2C.close()
