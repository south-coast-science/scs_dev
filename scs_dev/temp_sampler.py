#!/usr/bin/env python3

"""
Created on 2 Oct 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

Requires SystemID document.

command line example:
./temp_sampler.py -i 2 -n 10
"""

import sys

from scs_core.data.json import JSONify
from scs_core.data.localized_datetime import LocalizedDatetime

from scs_core.gas.pt1000_calib import Pt1000Calib

from scs_core.sample.sample_datum import SampleDatum

from scs_core.sync.timed_runner import TimedRunner

from scs_core.sys.exception_report import ExceptionReport
from scs_core.sys.system_id import SystemID

from scs_dev.cmd.cmd_sampler import CmdSampler
from scs_dev.sampler.temp_sampler import TempSampler

from scs_dfe.board.mcp9808 import MCP9808

from scs_dfe.climate.sht_conf import SHTConf

from scs_dfe.gas.pt1000 import Pt1000
from scs_dfe.gas.pt1000_conf import Pt1000Conf

from scs_host.bus.i2c import I2C
from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    cmd = None

    try:
        I2C.open(Host.I2C_SENSORS)

        # ------------------------------------------------------------------------------------------------------------
        # cmd...

        cmd = CmdSampler()

        if cmd.verbose:
            print(cmd, file=sys.stderr)


        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # SystemID...
        system_id = SystemID.load_from_host(Host)

        if system_id is None:
            print("SystemID not available.", file=sys.stderr)
            exit()

        if cmd.verbose:
            print(system_id, file=sys.stderr)

        # SHTs...
        sht_conf = SHTConf.load_from_host(Host)

        int_climate = sht_conf.int_sht()
        ext_climate = sht_conf.ext_sht()

        # Pt1000...
        pt1000_conf = Pt1000Conf.load_from_host(Host)
        pt1000_calib = Pt1000Calib.load_from_host(Host)
        pt1000 = Pt1000(pt1000_calib)

        board = MCP9808(True)

        # runner...
        runner = TimedRunner(cmd.interval, cmd.samples)

        # sampler...
        sampler = TempSampler(runner, int_climate, ext_climate, pt1000_conf, pt1000, board)

        if cmd.verbose:
            print(sampler, file=sys.stderr)
            sys.stderr.flush()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        for int_datum, ext_datum, pt1000_datum, board_datum, mcu_datum in sampler.samples():
            recorded = LocalizedDatetime.now()
            datum = SampleDatum(system_id.message_tag(), recorded, int_datum, ext_datum, pt1000_datum, board_datum,
                                mcu_datum)

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
