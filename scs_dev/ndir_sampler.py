#!/usr/bin/env python3

"""
Created on 27 Sep 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

command line example:
./ndir_sampler.py -i 2 -n 10
"""

import sys

from scs_core.data.json import JSONify
from scs_core.data.localized_datetime import LocalizedDatetime

from scs_core.sample.sample_datum import SampleDatum

from scs_core.sync.sampler import Sampler

from scs_core.sys.exception_report import ExceptionReport
from scs_core.sys.system_id import SystemID

from scs_dev.cmd.cmd_sampler import CmdSampler

from scs_host.sys.host import Host

from scs_ndir.gas.ndir_conf import NDIRConf


# --------------------------------------------------------------------------------------------------------------------

class NDIRSampler(Sampler):
    """
    classdocs
    """
    # ----------------------------------------------------------------------------------------------------------------

    # noinspection PyShadowingNames
    def __init__(self, ndir, interval, sample_count=None):
        """
        Constructor
        """
        Sampler.__init__(self, interval, sample_count)

        self.__ndir = ndir


    # ----------------------------------------------------------------------------------------------------------------

    def sample(self):
        return 'ndir', self.__ndir.sample()


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "NDIRSampler:{ndir:%s, timer:%s, sample_count:%d}" %  (self.__ndir, self.timer, self.sample_count)


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSampler()

    if cmd.verbose:
        print(cmd, file=sys.stderr)

    try:
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

        if ndir is None:
            print("NDIR not available.", file=sys.stderr)
            exit()

        if cmd.verbose:
            print(ndir, file=sys.stderr)

        # Sampler...
        sampler = NDIRSampler(ndir, cmd.interval, cmd.samples)

        if cmd.verbose:
            print(ndir, file=sys.stderr)
            sys.stderr.flush()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        for sample in sampler.samples():
            recorded = LocalizedDatetime.now()
            datum = SampleDatum(system_id.message_tag(), recorded, sample)

            print(JSONify.dumps(datum))
            sys.stdout.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt as ex:
        if cmd.verbose:
            print("ndir_sampler: KeyboardInterrupt", file=sys.stderr)

    except Exception as ex:
        print(JSONify.dumps(ExceptionReport.construct(ex)), file=sys.stderr)
