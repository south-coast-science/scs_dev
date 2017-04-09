#!/usr/bin/env python3

"""
Created on 3 Apr 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

Requires DeviceID document.

command line example:
./scs_dev/sht_sampler.py -i 0.1 -n 10
"""

import sys

from scs_core.data.json import JSONify
from scs_core.data.localized_datetime import LocalizedDatetime
from scs_core.sample.sample_datum import SampleDatum
from scs_core.sync.sampler import Sampler
from scs_core.sys.device_id import DeviceID
from scs_core.sys.exception_report import ExceptionReport

from scs_dev.cmd.cmd_sampler import CmdSampler

from scs_dfe.board.mcp9808 import MCP9808
from scs_dfe.climate.sht_conf import SHTConf

from scs_host.bus.i2c import I2C
from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

class SHTSampler(Sampler):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, climate, interval, sample_count=0):
        """
        Constructor
        """
        Sampler.__init__(self, interval, sample_count)

        self.__climate = climate

        self.__climate.reset()


    # ----------------------------------------------------------------------------------------------------------------

    def sample(self):
        return 'sht', self.__climate.sample()


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "SHTSampler:{timer:%s, sample_count:%d}" % (self.timer, self.sample_count)


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    cmd = None
    data = []

    try:
        I2C.open(Host.I2C_SENSORS)

        # ------------------------------------------------------------------------------------------------------------
        # cmd...

        cmd = CmdSampler()

        if cmd.verbose:
            print(cmd, file=sys.stderr)


        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # DeviceID...
        device_id = DeviceID.load_from_host(Host)

        if device_id is None:
            print("DeviceID not available.", file=sys.stderr)
            exit()

        if cmd.verbose:
            print(device_id, file=sys.stderr)

        # sampler...
        sht_conf = SHTConf.load_from_host(Host)

        int_climate = sht_conf.int_sht()        # TODO: parameterise this

        board = MCP9808(True)

        sampler = SHTSampler(int_climate, cmd.interval, cmd.samples)

        if cmd.verbose:
            print(sampler, file=sys.stderr)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        # sample...
        for int_datum in sampler.samples():
            recorded = LocalizedDatetime.now()
            datum = SampleDatum(device_id.message_tag(), recorded, int_datum)

            data.append(datum)

        # flush...
        for datum in data:
            print(JSONify.dumps(datum))
            sys.stdout.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt as ex:
        if cmd.verbose:
            print("sht_sampler: KeyboardInterrupt", file=sys.stderr)

    except Exception as ex:
        print(JSONify.dumps(ExceptionReport.construct(ex)), file=sys.stderr)

    finally:
        I2C.close()
