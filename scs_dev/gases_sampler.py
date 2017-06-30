#!/usr/bin/env python3

"""
Created on 5 Dec 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

Requires SystemID document.

Note: this script uses the internal SHT temp sensor for temperature compensation.

command line example:
./gases_sampler.py -i 5 | ./osio_topic_publisher.py -e /users/southcoastscience-dev/test/gases
"""

import sys

from scs_core.data.json import JSONify
from scs_core.data.localized_datetime import LocalizedDatetime

from scs_core.gas.afe_baseline import AFEBaseline
from scs_core.gas.afe_calib import AFECalib
from scs_core.gas.pt1000_calib import Pt1000Calib

from scs_core.sys.exception_report import ExceptionReport
from scs_core.sys.system_id import SystemID

from scs_dev.cmd.cmd_sampler import CmdSampler
from scs_dev.sampler.gases_sampler import GasesSampler

from scs_dfe.climate.sht_conf import SHTConf
from scs_dfe.gas.pt1000 import Pt1000
from scs_dfe.gas.pt1000_conf import Pt1000Conf

from scs_host.bus.i2c import I2C
from scs_host.sys.host import Host

from scs_ndir.gas.ndir_conf import NDIRConf


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

        # NDIR...
        ndir_conf = NDIRConf.load_from_host(Host)
        ndir = ndir_conf.ndir(Host)

        # SHT...
        sht_conf = SHTConf.load_from_host(Host)
        sht = sht_conf.int_sht()

        # Pt1000...
        pt1000_conf = Pt1000Conf.load_from_host(Host)
        pt1000_calib = Pt1000Calib.load_from_host(Host)
        pt1000 = Pt1000(pt1000_calib)

        # AFE...
        afe_baseline = AFEBaseline.load_from_host(Host)

        afe_calib = AFECalib.load_from_host(Host)
        sensors = afe_calib.sensors(afe_baseline)

        # SemaphoreSampler...
        sampler = GasesSampler(system_id, ndir, sht, pt1000_conf, pt1000, sensors, cmd.interval, cmd.samples)

        if cmd.verbose:
            print(sampler, file=sys.stderr)
            sys.stderr.flush()


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
