#!/usr/bin/env python3

"""
Created on 27 Sep 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

command line example:
./scs_dev/afe_sn_sampler.py -s 4 -i 0.5 -n 10
"""

import sys

from scs_core.data.json import JSONify
from scs_core.data.localized_datetime import LocalizedDatetime
from scs_core.sample.sample_datum import SampleDatum
from scs_core.sync.sampler import Sampler
from scs_core.sys.exception_report import ExceptionReport

from scs_dev.cmd.cmd_sn import CmdSN

from scs_dfe.bus.i2c import I2C
from scs_dfe.gas.afe import AFE
from scs_dfe.gas.afe_conf import AFEConf
from scs_dfe.gas.pt1000_calib import Pt1000Calib

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

class AFESNSampler(Sampler):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, pt1000, sensors, sn, interval, sample_count=0):
        """
        Constructor
        """
        Sampler.__init__(self, interval, sample_count)

        self.__sn = sn
        self.__afe = AFE(pt1000, sensors)


    # ----------------------------------------------------------------------------------------------------------------

    def sample(self):
        return 'afe', self.__afe.sample_station(self.__sn)


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "AFESNSampler:{afe:%s, sn:%d, timer:%s, sample_count:%d}" % \
                    (self.__afe, self.__sn, self.timer, self.sample_count)


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    calib = Pt1000Calib.load(Host)
    pt1000 = calib.pt1000()

    conf = AFEConf.load(Host)
    sensors = conf.sensors()


    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSN()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit()

    if cmd.verbose:
        print(cmd, file=sys.stderr)

    try:
        I2C.open(Host.I2C_SENSORS)


        # ------------------------------------------------------------------------------------------------------------
        # resource...

        afe = AFESNSampler(pt1000, sensors, cmd.sn, cmd.interval, cmd.samples)

        if cmd.verbose:
            print(afe, file=sys.stderr)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        for sample in afe.samples():
            recorded = LocalizedDatetime.now()
            datum = SampleDatum(recorded, sample)

            print(JSONify.dumps(datum))
            sys.stdout.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt as ex:
        if cmd.verbose:
            print("afe_sn_sampler: KeyboardInterrupt", file=sys.stderr)

    except Exception as ex:
        print(JSONify.dumps(ExceptionReport.construct(ex)), file=sys.stderr)

    finally:
        I2C.close()
