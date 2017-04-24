#!/usr/bin/env python3

"""
Created on 27 Sep 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

Requires SystemID document.

Note: this script uses the Pt1000 temp sensor for temperature compensation.

command line example:
./afe_sn_sampler.py -s 4 -i 0.5 -n 10
"""

import sys

from scs_core.data.json import JSONify
from scs_core.data.localized_datetime import LocalizedDatetime

from scs_core.gas.afe_baseline import AFEBaseline
from scs_core.gas.afe_calib import AFECalib
from scs_core.gas.pt1000_calib import Pt1000Calib

from scs_core.sample.sample_datum import SampleDatum

from scs_core.sync.sampler import Sampler

from scs_core.sys.exception_report import ExceptionReport
from scs_core.sys.system_id import SystemID

from scs_dev.cmd.cmd_sn import CmdSN

from scs_dfe.gas.afe import AFE
from scs_dfe.gas.pt1000 import Pt1000

from scs_host.bus.i2c import I2C
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
        # resources...

        # SystemID...
        system_id = SystemID.load_from_host(Host)

        if system_id is None:
            print("SystemID not available.", file=sys.stderr)
            exit()

        if cmd.verbose:
            print(system_id, file=sys.stderr)


        # sampler...
        calib = Pt1000Calib.load_from_host(Host)
        pt1000 = Pt1000(calib)

        afe_baseline = AFEBaseline.load_from_host(Host)

        calib = AFECalib.load_from_host(Host)
        sensors = calib.sensors(afe_baseline)

        afe = AFESNSampler(pt1000, sensors, cmd.sn, cmd.interval, cmd.samples)

        if cmd.verbose:
            print(afe, file=sys.stderr)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        for sample in afe.samples():
            recorded = LocalizedDatetime.now()
            datum = SampleDatum(system_id.message_tag(), recorded, sample)

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
