#!/usr/bin/env python3

'''
Created on 5 Dec 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

command line example:
./gases_sampler.py -i 5 | ./osio_topic_publisher.py -e /users/southcoastscience-dev/test/gases
'''

import sys

from scs_dfe.climate.sht_conf import SHTConf

from scs_dfe.gas.afe_conf import AFEConf
from scs_dfe.gas.pt1000_calib import Pt1000Calib

from scs_dev.cmd.cmd_scalar import CmdScalar
from scs_dev.sampler.gases_sampler import GasesSampler

from scs_dfe.bus.i2c import I2C

from scs_host.sys.host import Host

from scs_core.common.json import JSONify

from scs_core.sys.exception_report import ExceptionReport


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    sht_conf = SHTConf.load(Host)
    sht = sht_conf.ext_sht()            # TODO: this should be int_sht() but we don't have one yet

    calib = Pt1000Calib.load(Host)
    pt1000 = calib.pt1000()

    conf = AFEConf.load(Host)
    sensors = conf.sensors()


    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdScalar()

    if cmd.verbose:
        print(cmd, file=sys.stderr)

    try:
        I2C.open(Host.I2C_SENSORS)


        # ------------------------------------------------------------------------------------------------------------
        # resource...

        sampler = GasesSampler(sht, pt1000, sensors, cmd.interval, cmd.samples)

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
            print("gases_sampler: KeyboardInterrupt", file=sys.stderr)

    except Exception as ex:
        print(JSONify.dumps(ExceptionReport.construct(ex)), file=sys.stderr)

    finally:
        I2C.close()
