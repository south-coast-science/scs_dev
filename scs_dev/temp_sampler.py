#!/usr/bin/env python3

"""
Created on 2 Oct 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

command line example:
./scs_dev/temp_sampler.py -i 2 -n 10
"""

import sys

from scs_core.data.json import JSONify
from scs_core.data.localized_datetime import LocalizedDatetime
from scs_core.sample.sample_datum import SampleDatum
from scs_core.sync.sampler import Sampler
from scs_core.sys.exception_report import ExceptionReport

from scs_dev.cmd.cmd_scalar import CmdScalar

from scs_dfe.board.mcp9808 import MCP9808
from scs_dfe.climate.sht_conf import SHTConf
from scs_dfe.gas.afe import AFE
from scs_dfe.gas.pt1000_calib import Pt1000Calib

from scs_host.bus.i2c import I2C
from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

class TempSampler(Sampler):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, climate, pt1000, board, interval, sample_count=0):
        """
        Constructor
        """
        Sampler.__init__(self, interval, sample_count)

        self.__climate = climate
        self.__afe = AFE(pt1000, [])
        self.__board = board

        self.__climate.reset()


    # ----------------------------------------------------------------------------------------------------------------

    def sample(self):
        return ('sht', self.__climate.sample()), ('pt1', self.__afe.sample_temp()), ('brd', self.__board.sample()), ('host', Host.mcu_temp())


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "TempSampler:{timer:%s, sample_count:%d}" % (self.timer, self.sample_count)


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    cmd = None

    try:
        I2C.open(Host.I2C_SENSORS)

        # ------------------------------------------------------------------------------------------------------------
        # cmd...

        cmd = CmdScalar()

        if cmd.verbose:
            print(cmd, file=sys.stderr)


        # ------------------------------------------------------------------------------------------------------------
        # resource...

        sht_conf = SHTConf.load_from_host(Host)
        climate = sht_conf.ext_sht()

        calib = Pt1000Calib.load_from_host(Host)
        pt1000 = calib.pt1000()

        board = MCP9808(True)

        sampler = TempSampler(climate, pt1000, board, cmd.interval, cmd.samples)

        if cmd.verbose:
            print(sampler, file=sys.stderr)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        for sht_datum, pt1000_datum, board_datum, mcu_datum in sampler.samples():
            recorded = LocalizedDatetime.now()
            datum = SampleDatum(recorded, sht_datum, pt1000_datum, board_datum, mcu_datum)

            print(JSONify.dumps(datum))
            sys.stdout.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt as ex:
        if cmd.verbose:
            print("temp_sampler: KeyboardInterrupt", file=sys.stderr)

    except Exception as ex:
        print(JSONify.dumps(ExceptionReport.construct(ex)), file=sys.stderr)

    finally:
        I2C.close()
