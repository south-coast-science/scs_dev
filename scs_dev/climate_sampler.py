#!/usr/bin/env python3

"""
Created on 18 Feb 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

command line example:
./scs_dev/climate_sampler.py -i 5 | ./scs_dev/osio_topic_publisher.py -e /users/southcoastscience-dev/test/climate
"""

import sys

from scs_core.data.json import JSONify
from scs_core.sys.exception_report import ExceptionReport

from scs_dev.cmd.cmd_scalar import CmdScalar
from scs_dev.sampler.climate_sampler import ClimateSampler

from scs_dfe.climate.sht_conf import SHTConf

from scs_host.bus.i2c import I2C
from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    sht_conf = SHTConf.load_from_host(Host)
    sht = sht_conf.ext_sht()


    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdScalar()

    if cmd.verbose:
        print(cmd, file=sys.stderr)

    try:
        I2C.open(Host.I2C_SENSORS)


        # ------------------------------------------------------------------------------------------------------------
        # resource...

        sampler = ClimateSampler(sht, cmd.interval, cmd.samples)

        if cmd.verbose:
            print(sampler, file=sys.stderr)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        for sample in sampler.samples():
            print(JSONify.dumps(sample))
            sys.stdout.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt as ex:
        if cmd.verbose:
            print("climate_sampler: KeyboardInterrupt", file=sys.stderr)

    except Exception as ex:
        print(JSONify.dumps(ExceptionReport.construct(ex)), file=sys.stderr)

    finally:
        I2C.close()
