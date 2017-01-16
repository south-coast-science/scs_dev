#!/usr/bin/env python3

"""
Created on 5 Dec 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

command line example:
./particulates_sampler.py -i 10 | ./osio_topic_publisher.py -e /users/southcoastscience-dev/test/particulates
"""

import sys

from scs_core.data.json import JSONify
from scs_core.sys.exception_report import ExceptionReport

from scs_dev.cmd.cmd_scalar import CmdScalar
from scs_dev.sampler.particulates_sampler import ParticulatesSampler


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    sampler = None

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdScalar(10)

    if cmd.verbose:
        print(cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resource...

        sampler = ParticulatesSampler(cmd.interval, cmd.samples)

        if cmd.verbose:
            print(sampler, file=sys.stderr)

        sampler.on()
        sampler.reset_timer()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        for sample in sampler.samples():
            print(JSONify.dumps(sample))
            sys.stdout.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt as ex:
        if cmd.verbose:
            print("particulates_sampler: KeyboardInterrupt", file=sys.stderr)

    except Exception as ex:
        print(JSONify.dumps(ExceptionReport.construct(ex)), file=sys.stderr)

    finally:
        if sampler:
            sampler.off()
