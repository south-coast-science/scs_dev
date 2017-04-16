#!/usr/bin/env python3

"""
Created on 5 Dec 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

Requires SystemID document.

Note: this script uses the internal SHT temp sensor for temperature compensation.

command line example:
./scs_dev/gases_sampler.py -i 5 | ./scs_dev/osio_topic_publisher.py -e /users/southcoastscience-dev/test/gases
"""

import sys

from scs_core.data.json import JSONify
from scs_core.data.localized_datetime import LocalizedDatetime
from scs_core.sys.system_id import SystemID
from scs_core.sys.exception_report import ExceptionReport

from scs_dev.cmd.cmd_sampler import CmdSampler
from scs_dev.sampler.gases_sampler import GasesSampler

from scs_dfe.climate.sht_conf import SHTConf
from scs_dfe.gas.afe_baseline import AFEBaseline
from scs_dfe.gas.afe_calib import AFECalib
from scs_dfe.gas.pt1000_calib import Pt1000Calib

from scs_host.bus.i2c import I2C
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
        system_id = SystemID.load_from_host(Host)

        if system_id is None:
            print("SystemID not available.", file=sys.stderr)
            exit()

        if cmd.verbose:
            print(system_id, file=sys.stderr)


        sht_conf = SHTConf.load_from_host(Host)
        sht = sht_conf.int_sht()

        calib = Pt1000Calib.load_from_host(Host)
        pt1000 = calib.pt1000()

        afe_baseline = AFEBaseline.load_from_host(Host)

        calib = AFECalib.load_from_host(Host)
        sensors = calib.sensors(afe_baseline)

        sampler = GasesSampler(system_id, sht, pt1000, sensors, cmd.interval, cmd.samples)

        if cmd.verbose:
            print(sampler, file=sys.stderr)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        for sample in sampler.samples():
            if cmd.verbose:
                now = LocalizedDatetime.now()
                print("%s:        gases: %s" % (now.as_iso8601(), sample.rec.as_iso8601()), file=sys.stderr)
                sys.stderr.flush()

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
